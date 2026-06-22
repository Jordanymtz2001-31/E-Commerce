from abc import ABC, abstractmethod
from django.db.models import QuerySet


class FiltroProductoStrategy(ABC):
    """
    Estrategia abstracta para filtrar productos.

    Por qué Strategy Pattern: Permite agregar nuevos filtros (por talla,
    por materia, por rango de precio) sin modificar el código existente
    de las vistas — simplemente creando una nueva clase que herede de
    FiltroProductoStrategy.
    OCP: El sistema queda abierto a extensión (nuevas estrategias) pero
    cerrado a modificación (las vistas no cambian).
    """

    @abstractmethod
    def aplicar(self, queryset: QuerySet) -> QuerySet:
        """Aplica el filtro al queryset y retorna el resultado."""
        pass


class SinFiltro(FiltroProductoStrategy):
    """
    Estrategia nula: retorna el queryset sin modificaciones.

    Implementa el patrón Null Object para evitar condicionales
    (if/else) en las vistas cuando no hay filtro activo.
    
    Esto pasara cuando se ingrese a la vista de productos sin seleccionar una categoría, 
    y entonces no se aplicará ningún filtro y se mostrarán todos los productos.
    """

    def aplicar(self, queryset: QuerySet) -> QuerySet:
        return queryset


class FiltroPorCategoria(FiltroProductoStrategy):
    """Filtra productos por ID de categoría."""

    # Creamos un constructor para recibir el ID de categoría al instanciar la estrategia.
    def __init__(self, categoria_id: int):
        # Guardamos el ID de categoría como atributo de la instancia para usarlo en aplicar().
        self.categoria_id = categoria_id

    def aplicar(self, queryset: QuerySet) -> QuerySet:
        
        # Aplicamos el filtro al queryset usando el ID de categoría guardado en la instancia para compararlo con el campo categoria__id de los productos. 
        # Esto devuelve solo los productos que pertenecen a la categoría especificada.
        return queryset.filter(categoria__id=self.categoria_id)


class FiltroPorColor(FiltroProductoStrategy):
    """Filtra productos por ID de color."""

    def __init__(self, color_id: int):
        self.color_id = color_id

    def aplicar(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(color__id=self.color_id)
