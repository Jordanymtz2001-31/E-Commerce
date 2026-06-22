from django.db import models
from django.db.models import QuerySet, Prefetch
from django.shortcuts import get_object_or_404
from .models import Categoria, Producto, PuntoVenta, Evento, Pedido, DetallePedido


class ProductoRepository:
    """
    Repositorio para el acceso a datos de Producto.

    DIP: Las vistas dependen de este repositorio (abstracción) en vez de
    llamar a Producto.objects.filter(...) directamente. Si en el futuro se
    agrega caché (Redis) o se cambia el ORM, solo se modifica este archivo.
    OCP: Agregar un nuevo método de consulta (ej: buscar_por_precio) no
    requiere modificar las vistas existentes.
    """

    def listar_con_stock(self, categoria_id: int = None) -> QuerySet:
        """
        Para listados que solo necesitan el stock total (sin desglose por talla).

        Usa annotate + Sum('talla_stock') para calcular stock_disponible en
        la propia consulta SQL, evitando el N+1 que ocurriría si cada producto
        hiciera un aggregate() individual.
        El valor anotado queda disponible como producto.stock_total y la
        property stock_disponible lo usa automáticamente.
        """
        qs = Producto.objects.prefetch_related(
            'imagenes',
            'categoria',
            'tallaDisponible',
            'tipoMateria',
            'color',
        ).annotate(
            stock_total=models.Sum('stocktalla_set__talla_stock'),
        )
        if categoria_id:
            qs = qs.filter(categoria__id=categoria_id)
        return qs

    def listar_con_desglose_tallas(self, categoria_id: int = None) -> QuerySet:
        """
        Para listados que SÍ necesitan el detalle stock por talla en la UI
        (ej: stock_por_talla en la tarjeta del producto).

        Usa prefetch_related('stocktalla_set__talla') para cargar TODOS los
        StockTalla + Talla en 2 consultas fijas, sin importar cuántos
        productos haya. Sin esto, producto.stocktalla_set.filter() dentro
        de un bucle generaría N consultas adicionales.
        """
        qs = Producto.objects.prefetch_related(
            'imagenes',
            'categoria',
            'tallaDisponible',
            'tipoMateria',
            'instruccionesCuidado',
            'color',
            'stocktalla_set__talla',
        )
        if categoria_id:
            qs = qs.filter(categoria__id=categoria_id)
        return qs

    # Alias semántico: prefetch_related es correcto para el desglose
    listar_con_relaciones = listar_con_desglose_tallas

    def filtrar_por_categoria(self, queryset: QuerySet, categoria_id: int) -> QuerySet:
        
        return queryset.filter(categoria__id=categoria_id)

    def obtener_por_categoria(self, categoria_id: int) -> QuerySet:
        return self.listar_con_desglose_tallas(categoria_id=categoria_id)


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
            Prefetch('detalles', queryset=DetallePedido.objects.select_related('producto', 'Talla')),
        ).filter(cliente=cliente)
        return get_object_or_404(qs, pk=pk)
