from django.db import models
from django.db.models import QuerySet, Prefetch
from django.shortcuts import get_object_or_404
from .models import Categoria, Producto, PuntoVenta, Evento, Pedido, DetallePedido, VarianteProducto


class ProductoRepository:

    def listar_con_variantes(self, categoria_id: int = None) -> QuerySet:
        
        # Cargamos varias relaciones en una sola consulta
        # Tambien las variantes pero solo las activas y relaciones con talla y color
        qs = Producto.objects.prefetch_related(
            'imagenes',
            'categoria',
            'tipoMateria',
            'instruccionesCuidado',
            Prefetch(
                'variantes',
                queryset=VarianteProducto.objects.filter(activo=True).select_related('color', 'talla'),
            ),
        ).annotate( # Creamos campos auxiliares para hacer consultas mas eficientes
            stock_total=models.Sum('variantes__stock', filter=models.Q(variantes__activo=True)), # Suma el stock de todas las variantes activas
            precio_min=models.Min('variantes__precio', filter=models.Q(variantes__activo=True)), # Minimo de todas las variantes activas
            precio_max=models.Max('variantes__precio', filter=models.Q(variantes__activo=True)), # Maximo de todas las variantes activas
        )
        
        # Si hay un id de categoria, filtramos por ella
        if categoria_id:
            qs = qs.filter(categoria__id=categoria_id)
        return qs

    # Creamos un alias para cuando otro metodo lo llame ejecute este metodo
    listar_con_relaciones = listar_con_variantes

    def filtrar_por_categoria(self, queryset: QuerySet, categoria_id: int) -> QuerySet:
        return queryset.filter(categoria__id=categoria_id)

    def obtener_por_categoria(self, categoria_id: int) -> QuerySet:
        return self.listar_con_variantes(categoria_id=categoria_id)


class CategoriaRepository:
    """Repositorio para acceso a datos de Categoria."""

    def listar_todas(self) -> QuerySet:
        return Categoria.objects.all()


class PuntoVentaRepository:
    """Repositorio para acceso a datos de PuntoVenta."""

    def listar_activos(self) -> QuerySet:
        return PuntoVenta.objects.filter(activo=True)


class EventoRepository:
    """
    Repositorio para acceso a datos de Evento.

    Centraliza la lógica de separación entre eventos próximos y pasados
    para que cualquier vista o comando que necesite eventos use la misma
    consulta.
    """

    def listar_proximos(self, fecha) -> QuerySet:
        return (
            Evento.objects
            .filter(activo=True, fecha__gte=fecha)
            .prefetch_related('fotos', 'colaboradores')
            .order_by('fecha')
        )

    def listar_pasados(self, fecha) -> QuerySet:
        return (
            Evento.objects
            .filter(activo=True, fecha__lt=fecha)
            .prefetch_related('fotos', 'colaboradores')
            .order_by('-fecha')
        )


class PedidoRepository:
    """Repositorio para acceso a datos de Pedido."""

    def listar_por_cliente(self, cliente) -> QuerySet:
        """
        Esta fucnion devuelve los pedidos de un cliente con sus detalles ya cargados para evitar el problema de N+1 consultas al acceder a pedido.detalles en la vista.
        Prefetch_related con Prefetch nos permite cargar los detalles de cada pedido en una consulta separada pero eficiente, 
        y select_related dentro del Prefetch carga el producto y la talla de cada detalle en la misma consulta, evitando consultas adicionales al acceder a detalle.producto o detalle.Talla en la vista. 
        El resultado es que al iterar sobre los pedidos y sus detalles en la vista, no se generan consultas adicionales a la base de datos, ya que toda la información necesaria ya está cargada en memoria.
        """
        return (
            Pedido.objects
            .filter(cliente=cliente)
            .prefetch_related(
                Prefetch('detalles', queryset=DetallePedido.objects.select_related('producto', 'Talla')),
            )
            .order_by('-creado')
        )

    def obtener_con_detalles(self, pk: int, cliente) -> Pedido:
        """
        Obtiene un pedido por su ID, asegurando que los detalles estén precargados para evitar consultas adicionales en la vista. 
        """
        
        qs = Pedido.objects.prefetch_related(
            Prefetch('detalles', queryset=DetallePedido.objects.select_related('producto', 'Talla', 'variante')),
        ).filter(cliente=cliente)
        return get_object_or_404(qs, pk=pk)


# Repositorio para acceder a datos de VarianteProducto (Aun sin uso)
class VarianteProductoRepository:

    def listar_activas_por_producto(self, producto_id: int):
        return VarianteProducto.objects.filter(
            producto_id=producto_id, activo=True
        ).select_related('color', 'talla')

    def listar_activas_por_productos(self, producto_ids: list):
        return VarianteProducto.objects.filter(
            producto_id__in=producto_ids, activo=True
        ).select_related('color', 'talla')
