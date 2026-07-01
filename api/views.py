import json
import stripe
import logging

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


def _safe_url(image_field):
    try:
        return image_field.url if image_field else None
    except (ValueError, AttributeError):
        return None
from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import Paginator # Para la paginación

from .forms import RegistroForm
from .models import Categoria, Cliente, Producto, Pedido, Talla, Color
from .service import ClienteService, ResenaService, PedidoService, StripeService

logger = logging.getLogger(__name__)
from .repositories import (
    ProductoRepository,
    CategoriaRepository,
    PuntoVentaRepository,
    EventoRepository,
    PedidoRepository,
    VarianteProductoRepository,
)
from .strategies import SinFiltro, FiltroPorCategoria, FiltroPorColor


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
    """
    Lista productos por categoría con paginación de 20 por página.
    """
    categoria_seleccionada = get_object_or_404(Categoria, id=categoria_id)

    repo = ProductoRepository()
    categoria_repo = CategoriaRepository()

    productos = repo.obtener_por_categoria(categoria_id=categoria_id)
    categorias = categoria_repo.listar_todas()

    # Paginación: 20 productos por página
    paginator = Paginator(productos, 20)
    page_number = request.GET.get('page') # Obtiene el parámetro 'page' de la URL para la paginación
    page_obj = paginator.get_page(page_number) # Obtiene la página actual

    # Asignar variantes_data solo a los productos de la página actual
    for producto in page_obj:
        
        # Creamos una lista comprehension, esto se trabaja de otra forma    
        # 1 .Creamos el atributo dinamico(variantes_data) en el objeto producto como auxiliar
        producto.variantes_data = [
            
            # 2. Definimos que forma toma la informacion
            {
                'sku': v.sku,
                'color': {'nombre': v.color.nombre, 'hex': v.color.codigo_hex} if v.color else None,
                'talla': v.talla.nombreTalla if v.talla else None,
                'stock': v.stock,
                'precio': float(v.precio),
                'imagen': _safe_url(v.imagen),
            }
            
            # 3. Definimos la condicion y indicamos de donde tomar la informacion
            for v in producto.variantes.all()
        ]

    """
    Query string base para preservar filtros en paginación
    
    Es decir que si el usuario navega entre las paginas, se conservan los filtros 
    de categoria y color, esto con el fin de no perder la seleccion de categoria y color.
    De lo contrario cargaria todos los productos de la tienda.
    """
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    base_query_string = query_params.urlencode()

    context = {
        'productos': page_obj,
        'page_obj': page_obj,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
        'base_query_string': base_query_string,
    }
    return render(request, 'productos.html', context)

def productos_view(request):
    """
    Usa ProductoRepository para el acceso a datos y FiltroProductoStrategy
    para el filtro por categoría. Esto permite agregar nuevos filtros sin
    modificar esta vista (OCP).

    Paginación: 20 productos por página. Los filtros (?categoria, ?color)
    se conservan al navegar entre páginas (?page=N).
    """
    repo = ProductoRepository()
    categoria_repo = CategoriaRepository()

    productos = repo.listar_con_variantes()
    categorias = categoria_repo.listar_todas()
    colores = Color.objects.all()

    categoria_id = request.GET.get('categoria')
    color_id = request.GET.get('color')

    categoria_seleccionada = None
    color_seleccionado = None

    if categoria_id:
        categoria_seleccionada = get_object_or_404(Categoria, id=categoria_id)
        strategy = FiltroPorCategoria(categoria_seleccionada.id)
    elif color_id:
        color_seleccionado = get_object_or_404(Color, id=color_id)
        strategy = FiltroPorColor(color_seleccionado.id)
    else:
        # Null Object Pattern: evita el if/else en la llamada a aplicar()
        strategy = SinFiltro()

    productos_filtrados = strategy.aplicar(productos)

    # Paginación: 20 productos por página
    paginator = Paginator(productos_filtrados, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Asignar variantes_data solo a los productos de la página actual
    for producto in page_obj:
        producto.variantes_data = [
            {
                'sku': v.sku,
                'color': {'nombre': v.color.nombre, 'hex': v.color.codigo_hex} if v.color else None,
                'talla': v.talla.nombreTalla if v.talla else None,
                'stock': v.stock,
                'precio': float(v.precio),
                'imagen': _safe_url(v.imagen),
            }
            for v in producto.variantes.all()
        ]

    """
    Query string base para preservar filtros en paginación
    
    Es decir que si el usuario navega entre las paginas, se conservan los filtros 
    de categoria y color, esto con el fin de no perder la seleccion de categoria y color.
    De lo contrario cargaria todos los productos de la tienda.
    """
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    base_query_string = query_params.urlencode()

    context = {
        'productos': page_obj,
        'page_obj': page_obj,
        'categorias': categorias,
        'colores': colores,
        'categoria_seleccionada': categoria_seleccionada,
        'color_seleccionado': color_seleccionado,
        'base_query_string': base_query_string,
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

    # Manejar cancelación de pago desde Stripe
    cancelado = request.GET.get('cancelado')
    pedido_id = request.GET.get('pedido_id')
    if cancelado and pedido_id:
        try:
            pedido = Pedido.objects.get(pk=pedido_id, cliente=cliente, estado='PENDIENTE')
            PedidoService.restaurar_stock(pedido)
            messages.info(request, 'Pago cancelado. El stock ha sido liberado.')
        except Pedido.DoesNotExist:
            pass

    repo_categoria = CategoriaRepository()
    categorias = repo_categoria.listar_todas()

    if request.method == 'POST':
        # Validación de Stripe para el caso de que no esté activo (BETA)
        if not settings.STRIPE_ENABLED:
            messages.info(request, 'El sistema de pago estará disponible próximamente.')
            return redirect('productList')
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
            return redirect(StripeService.crear_session_checkout(pedido, request))
        
        # Capturamos las excepciones de Stripe que pueden ocurrir en la capa de negocio y redirigimos al usuario a la vista de checkout con un mensaje de error.
        except stripe.error.StripeError as e:
            logger.error(f'Error al crear la sesión de Stripe: {e}')
            if pedido:
                PedidoService.restaurar_stock(pedido)
            messages.error(request, 'Error al procesar el pago, Intentalo de nuevo.')
            return redirect('checkout')
        
        # Captura de excepciones del producto y talla
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
    
    # Verificar el pago con Stripe
    session_id = request.GET.get('session_id')
    if session_id and pedido.estado == 'PENDIENTE':
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid': # SI el pago fue exitoso
                # Actualizamos el estado del pedido a "PAGO EXITOSO"
                pedido.estado = 'PAGADO'
                pedido.save(update_fields=['estado']) # update_fields indica que solo actualizaremos el campo "estado"   
        except stripe.error.StripeError as e:
            messages.error(request, f'Error al verificar el pago: {e}')
            return redirect('tienda')
        
    context = {
        'pedido': pedido,
        'categorias': categorias,
        'pago_exitoso': True,
    }
    return render(request, 'pedido_confirmado.html', context)



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

    elif event['type'] == 'checkout.session.expired': # Si el evento es de una sesión expirada
        session = event['data']['object']
        try:
            pedido = Pedido.objects.get(stripe_id_sesion=session['id'], estado='PENDIENTE')
            PedidoService.restaurar_stock(pedido)
            logger.info(f"Pedido {pedido.id} — sesión expirada, stock restaurado")
        except Pedido.DoesNotExist:
            pass

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
