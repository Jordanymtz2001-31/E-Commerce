import json
import stripe
import logging

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings

from .forms import RegistroForm
from .models import Categoria, Cliente, Producto, Pedido, Talla
from .service import ClienteService, ResenaService, PedidoService, StripeService

logger = logging.getLogger(__name__)
from .repositories import (
    ProductoRepository,
    CategoriaRepository,
    PuntoVentaRepository,
    EventoRepository,
    PedidoRepository,
)
from .strategies import SinFiltro, FiltroPorCategoria


def registro_view(request):
    """
    Las vistas ahora delegan la lógica de negocio a servicios y el acceso
    a datos a repositorios. Esto mantiene SRP (la vista solo orquesta) y
    DIP (depende de abstracciones, no de modelos concretos).
    """
    categorias = CategoriaRepository().listar_todas()

    if request.method == 'POST':
        formulario = RegistroForm(request.POST)
        if formulario.is_valid():
            ClienteService.registrar(formulario.cleaned_data)
            messages.success(request, 'Usuario registrado correctamente!')
            return redirect('login')
    else:
        formulario = RegistroForm()

    return render(request, 'registro.html', {'form': formulario, 'categorias': categorias})


def login_view(request):
    categorias = CategoriaRepository().listar_todas()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Verifica si viene de una pagina protegida (con @login_required) y redirige ahí, sino a la tienda
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            messages.success(request, 'Inicio de sesion exitoso!')
            return redirect('tienda')
        else:
            messages.warning(request, 'Credenciales incorrectas.')

    return render(request, 'login.html', {'categorias': categorias})


def logout_view(request):
    logout(request)
    return redirect('tienda')


def tienda_view(request):
    categorias = CategoriaRepository().listar_todas()
    return render(request, 'tienda.html', {'categorias': categorias})


def productos_por_categoria(request, categoria_id):
    categoria_seleccionada = get_object_or_404(Categoria, id=categoria_id)
    
    repo = ProductoRepository()
    categoria_repo = CategoriaRepository()
    
    productos = repo.obtener_por_categoria(categoria_id=categoria_id)
    categorias = categoria_repo.listar_todas()
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
    }
    return render(request, 'productos.html', context)

def productos_view(request):
    """
    Usa ProductoRepository para el acceso a datos y FiltroProductoStrategy
    para el filtro por categoría. Esto permite agregar nuevos filtros sin
    modificar esta vista (OCP).
    """
    repo = ProductoRepository()
    categoria_repo = CategoriaRepository()

    # Usamos listar_con_desglose_tallas porque la vista necesita el detalle
    # stock por talla (stock_por_talla). Si solo se necesitara el total,
    # usaríamos listar_con_stock() que usa annotate + Sum en SQL.
    productos = repo.listar_con_desglose_tallas()
    categorias = categoria_repo.listar_todas()

    categoria_id = request.GET.get('categoria')
    if categoria_id:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        strategy = FiltroPorCategoria(categoria.id)
        categoria_seleccionada = categoria
    else:
        # Null Object Pattern: evita el if/else en la llamada a aplicar()
        strategy = SinFiltro()
        categoria_seleccionada = None

    productos_filtrados = strategy.aplicar(productos)

    for producto in productos_filtrados:
        
        # all() para cargar el queryset completo de StockTalla en memoria, evitando consultas adicionales dentro del bucle. 
        # Luego filtramos en Python para obtener solo los que tienen stock > 0.
        stock = [s for s in producto.stocktalla_set.all()]
        producto.stock_por_talla = [
            {'talla': s.talla.nombreTalla, 'stock': s.talla_stock}
            for s in stock
        ]

    context = {
        'productos': productos_filtrados,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
    }
    return render(request, 'productos.html', context)


@login_required
def crear_resena(request, pk):
    """
    Delega la creación de la reseña a ResenaService para mantener
    la lógica de validación y persistencia fuera de la vista (SRP).
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        try:
            cliente = get_object_or_404(Cliente, usuario=request.user)
            estrellas = int(request.POST.get('estrellas', 5))
            comentario = request.POST.get('comentario', '').strip()

            ResenaService.crear(
                producto=producto,
                usuario=cliente,
                estrellas=estrellas,
                comentario=comentario,
            )
            messages.success(request, '¡Gracias por tu reseña!')
        except (ValueError, Cliente.DoesNotExist):
            messages.error(request, 'Error en los datos enviados. Intentalo de nuevo')

    return redirect('productList')


def punto_venta_view(request):
    categoria_repo = CategoriaRepository()
    punto_venta_repo = PuntoVentaRepository()

    context = {
        'categorias': categoria_repo.listar_todas(),
        'puntos_venta': punto_venta_repo.listar_activos(),
    }
    return render(request, 'puntos_venta.html', context)


#@login_required
def checkout_view(request):
    
    """
    Muestra el resumen del carrito y permite crear el pedido.

    GET: Muestra formulario con resumen del carrito (leído desde localStorage
    en el frontend). POST: Crea el Pedido + DetallePedido via PedidoService.
    """
    
    # Deforma manual verificamos si esta authenticado para mostrar un mensaje personalizado y redirigir a login con next, en lugar de usar @login_required que redirige automáticamente a LOGIN_URL sin mensaje.
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para finalizar tu compra.')
        return redirect(f'/talcahualme/login/?next={request.path}')  # Redirige a login y luego vuelve a checkout
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Completa tu perfil de cliente antes de comprar.')
        return redirect('tienda')

    repo_categoria = CategoriaRepository()
    categorias = repo_categoria.listar_todas()

    if request.method == 'POST':
        cart_data = request.POST.get('cart_data', '[]') # Si no se envia, se envia un array vacio
        try:
            item = json.loads(cart_data) # Esperamos un JSON con la estructura: [{producto_id, talla, cantidad}, ...]
        except json.JSONDecodeError:
            messages.error(request, 'Error al procesar el carrito.')
            return redirect('productList')

        if not item:
            messages.warning(request, 'Tu canasto está vacío.')
            return render(request, 'checkout.html', {'cliente': cliente, 'categorias': categorias})

        try:
            # Llamamos a la capa de negocio para crear el pedido. Esto incluye la creación del Pedido, los DetallePedido y el cálculo del total. Si algo falla (producto no existe, talla no válida, etc), se lanzará una excepción y no se creará un pedido a medio hacer.
            # Tambien llamamos a StripeService para crear la sesión de checkout y obtener la URL a la que redirigir al usuario para que complete el pago. Esto mantiene la lógica de integración con Stripe encapsulada en un servicio, facilitando el mantenimiento y testing.
            pedido = PedidoService.crear(cliente=cliente, productos=item)
            stripe_url = StripeService.crear_session_checkout(pedido, request)
            return redirect(stripe_url)
        except Producto.DoesNotExist:
            messages.error(request, 'Uno de los productos ya no está disponible.')
            return redirect('productList')
        except Talla.DoesNotExist:
            messages.error(request, 'Talla no válida.')
            return redirect('productList')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('productList')
        
    context = {
        'cliente': cliente,
        'categorias': categorias,
    }

    return render(request, 'checkout.html', context)


@login_required
def pago_exitoso_view(request, pk):
    """Muestra confirmación después de un pago exitoso en Stripe."""
    repo_categoria = CategoriaRepository()
    categorias = repo_categoria.listar_todas()

    try:
        cliente = Cliente.objects.get(usuario=request.user)
        pedido = Pedido.objects.get(pk=pk, cliente=cliente)
    except (Cliente.DoesNotExist, Pedido.DoesNotExist):
        messages.error(request, 'Pedido no encontrado.')
        return redirect('tienda')

    return render(request, 'pedido_confirmado.html', {
        'pedido': pedido,
        'categorias': categorias,
        'pago_exitoso': True,
    })


@csrf_exempt # Stripe no envia el csrf token como un navegador normal, esta pensado para recibir peticiones automaticas de stripe
def stripe_webhook_view(request):
    """
    Endpoint para que Stripe notifique eventos (checkout.session.completed).
    Basicamente ocurre cuando un cliente completa el proceso de pago.
    
    Pero stripe manda un mensaje de confirmacion pero no en el navegador, por ende se manda en el webhook (esta vista)
    Y al mismo validamos y cambiamos el estado del pedido
        
    payload: El cuerpo del mensaje que Stripe envía.
    sig_header: La firma que Stripe envía en los headers para verificar que el webhook es de Stripe.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # Verificamos la firma del webhook
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed': # Si el evento es de un checkout completado
        session = event['data']['object'] # Obtenemos la sesión de Stripe
        try:
            pedido = Pedido.objects.get(stripe_id_sesion=session['id']) # Buscamos el pedido asociado a la sesión
            pedido.estado = 'PAGADO'
            pedido.save(update_fields=['estado'])
            logger.info(f"Pedido {pedido.id} marcado como PAGADO via webhook")
        except Pedido.DoesNotExist:
            logger.warning(f"Webhook: Pedido no encontrado para sesion {session['id']}")

    return HttpResponse(status=200)


@login_required
def pedido_confirmado_view(request, pk):
    """Muestra la confirmación de un pedido."""
    
    pedido_repo = PedidoRepository()
    repo_categoria = CategoriaRepository()
    categorias = repo_categoria.listar_todas()
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        pedido = pedido_repo.obtener_con_detalles(pk=pk, cliente=cliente)
    except (Cliente.DoesNotExist, Pedido.DoesNotExist):
        messages.error(request, 'Pedido no encontrado.')
        return redirect('tienda')

    context = {
        'pedido': pedido,
        'categorias': categorias,
    }
    return render(request, 'pedido_confirmado.html', context)


@login_required
def mis_pedidos_view(request):
    """Lista los pedidos del usuario autenticado."""
    
    repor_categoria = CategoriaRepository()
    categorias = repor_categoria.listar_todas()
    
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Completa tu perfil de cliente primero.')
        return redirect('tienda')

    pedido_repo = PedidoRepository()
    pedidos = pedido_repo.listar_por_cliente(cliente)
    
    context = {
        'pedidos': pedidos,
        'categorias': categorias,
    }

    return render(request, 'mis_pedidos.html', context)


def eventos_view(request):
    categoria_repo = CategoriaRepository()
    evento_repo = EventoRepository()
    hoy = timezone.now().date()

    context = {
        'categorias': categoria_repo.listar_todas(),
        'proximos': evento_repo.listar_proximos(hoy),
        'pasados': evento_repo.listar_pasados(hoy),
    }
    return render(request, 'eventos.html', context)
