from django.contrib import admin
from django.dispatch import receiver
from django.forms import BaseInlineFormSet, ValidationError
from django.db.models import Sum
from django.utils.html import format_html

# Regrsitramos nuestro modelos en el panel del administrador que puede ver los datos y realizar operaciones
from .models import InstruccionesCuidado, Producto, Categoria, Cliente, Resena, StockTalla, Talla, TipoMateria, PuntoVenta, Colaborador, Evento, FotoEvento, ImagenProducto, Color

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

    # Funcion para mostrar el color
    def mostrar_color(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;background:{};border-radius:50%;border:1px solid #ccc;"></span>',
            obj.codigo_hex
        )
    mostrar_color.short_description = 'Muestra'

class StockTallaFormSet(BaseInlineFormSet):
    pass

#Clase para agregar mas de una imagen del producto
class FotoProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ['imagenes']

class StockTallaInline(admin.TabularInline):
    model = StockTalla
    formset = StockTallaFormSet # Agregamos la clase de StockTallaFormSet
    extra = 1  # Esto es para que se muestre un formulario extra
    fields = ['talla', 'talla_stock']  # Solo estos campos
    
    
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock_tallas', 'descripcion']
    list_filter = ['categoria'] # Estos son los campos de filtro
    search_fields = ['nombre'] # Estos son los campos de busqueda
    filter_horizontal = ['color', 'categoria', 'tallaDisponible', 'tipoMateria', 'instruccionesCuidado'] # Estos son los campos de filtro horizontal para que se pase la informacion de una tabla a otra
    inlines = [StockTallaInline, FotoProductoInline]  # Aqui agregamos la clase de StockTallaInline  y la clase de FotoProductoInline

    def stock_tallas(self, obj):
        return StockTalla.objects.filter(producto=obj).aggregate(
            total=Sum('talla_stock')
        )['total'] or 0
    stock_tallas.short_description = 'Stock Total'

@admin.register(Resena)
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'estrellas', 'comentario', 'fecha']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'direccion'] # Estos son los campos a mostrar en el administrador en la tabla
    search_fields = ['usuario']


@admin.register(PuntoVenta)
class PuntoVentaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'telefono', 'es_principal', 'activo'] # Estos son los campos a mostrar en el administrador en la tabla
    list_filter = ['activo', 'es_principal'] # Estos son los campos de filtro
    search_fields = ['nombre', 'ciudad'] # Estos son los campos de busqueda
    list_editable = ['activo'] # Estos son los campos que se pueden editar

# Clase para mostrar las fotos de los eventos
class FotoEventoInline(admin.TabularInline):
    model = FotoEvento
    extra = 1
    fields = ['foto', 'descripcion']

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
    es_proximo.short_description = '¿Próximo?'
