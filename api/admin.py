from django.contrib import admin
from django.db.models import Min, Max, Sum
from django.utils.html import format_html

from .models import (
    Categoria, Cliente, Colaborador, Color, Evento, FotoEvento,
    ImagenProducto, InstruccionesCuidado, Pedido, Producto, PuntoVenta,
    Resena, Talla, TipoMateria, VarianteProducto,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombreCategoria']


@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    search_fields = ['nombreTalla']
    list_display = ['nombreTalla']


@admin.register(TipoMateria)
class TipoMateriaAdmin(admin.ModelAdmin):
    list_display = ['nombreTipoMateria']


@admin.register(InstruccionesCuidado)
class InstruccionesCuidadoAdmin(admin.ModelAdmin):
    list_display = ['nombre']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo_hex', 'mostrar_color']
    search_fields = ['nombre']

    # Funcion para mostrar el color
    def mostrar_color(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;background:{};border-radius:50%;border:1px solid #ccc;"></span>',
            obj.codigo_hex
        )
    mostrar_color.short_description = 'Muestra'


#Clase para agregar mas de una imagen del producto en general
class FotoProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ['imagenes']


class VarianteProductoInline(admin.TabularInline):
    model = VarianteProducto
    extra = 1
    fields = ['color', 'talla', 'precio', 'stock', 'imagen', 'activo']
    readonly_fields = ['sku'] # readonly_fields es para que no se pueda editar
    autocomplete_fields = ['color', 'talla']


@admin.register(VarianteProducto)
class VarianteProductoAdmin(admin.ModelAdmin):
    list_display = ['sku', 'producto', 'color', 'talla', 'precio', 'stock', 'activo']
    list_filter = ['activo', 'color', 'talla']
    search_fields = ['sku', 'producto__nombre']
    readonly_fields = ['sku'] # readonly_fields es para que no se pueda editar


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio_base', 'rango_precios', 'stock_variantes', 'descripcion']
    list_filter = ['categoria']
    search_fields = ['nombre']
    filter_horizontal = ['categoria', 'tipoMateria', 'instruccionesCuidado']
    inlines = [FotoProductoInline, VarianteProductoInline]
    fieldsets = [
        (None, {
            'fields': ['nombre', 'precio_base', 'descripcion', 'categoria', 'tipoMateria', 'instruccionesCuidado']
        }),
    ]

    # Metodo para mostrar el rango de precios en el administrador
    def rango_precios(self, obj):
        precios = VarianteProducto.objects.filter(producto=obj, activo=True).aggregate(
            min=Min('precio'), max=Max('precio')
        )
        if precios['min'] is None:
            return '-'
        if precios['min'] == precios['max']:
            return f"${precios['min']:.0f}"
        return f"${precios['min']:.0f} - ${precios['max']:.0f}"
    rango_precios.short_description = 'Precio'

    # Metodo para mostrar el stock total de las variantes en el administrador
    def stock_variantes(self, obj):
        total = VarianteProducto.objects.filter(producto=obj).aggregate(
            total=Sum('stock')
        )['total'] or 0
        return total
    stock_variantes.short_description = 'Stock Total'


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'estrellas', 'comentario', 'fecha']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'direccion'] # Estos son los campos a mostrar en el administrador en la tabla
    search_fields = ['usuario']


class FotoEventoInline(admin.TabularInline):
    model = FotoEvento
    extra = 1
    fields = ['foto', 'descripcion']


@admin.register(PuntoVenta)
class PuntoVentaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'telefono', 'es_principal', 'activo']
    list_filter = ['activo', 'es_principal']
    search_fields = ['nombre', 'ciudad']
    list_editable = ['activo']


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'url']
    search_fields = ['nombre']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha', 'lugar', 'es_proximo', 'activo']
    list_filter = ['activo', 'fecha']
    search_fields = ['nombre', 'lugar']
    list_editable = ['activo']
    filter_horizontal = ['colaboradores']
    inlines = [FotoEventoInline]

    #Metodo para mostrar si el evento es próximo
    def es_proximo(self, obj):
        return obj.es_proximo
    es_proximo.boolean = True
    es_proximo.short_description = '\u00bfPr\u00f3ximo?'
