from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import RegistroForm
from .models import Categoria, Cliente, Producto
from .service import ClienteService, ResenaService
from .repositories import (
    ProductoRepository,
    CategoriaRepository,
    PuntoVentaRepository,
    EventoRepository,
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
        stock = [s for s in producto.stocktalla_set.all() if s.talla_stock > 0]
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