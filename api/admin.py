from django.contrib import admin
from django.dispatch import receiver
from django.forms import BaseInlineFormSet, ValidationError
from django.db.models import Sum

# Regrsitramos nuestro modelos en el panel del administrador que puede ver los datos y realizar operaciones
from .models import InstruccionesCuidado, Producto, Categoria, Cliente, Resena, StockTalla, Talla, TipoMateria, PuntoVenta, Colaborador, Evento, FotoEvento, ImagenProducto

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

#Creamos esta clases para validar el stock total de las tallas que se agregan
class StockTallaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        # OBTENER stock FÍSICO del producto
        stock_fisico = self.instance.stockProducto

        # SUMAR SOLO tallas con stock > 0
        stock_usado = 0
        for form in self.forms:
            if hasattr(form, 'cleaned_data') and form.cleaned_data:
                talla_stock = form.cleaned_data.get('talla_stock', 0)
                if talla_stock > 0:
                    stock_usado += talla_stock
        
        # VALIDAR que NO exceda lo físico
        if stock_usado > stock_fisico:
            excedente = stock_usado - stock_fisico
            raise ValidationError(
                f"Stock total ({stock_usado}) excede stock físico ({stock_fisico}). "
                f"Reduce {excedente} unidades, ya que solo se mostraran {stock_fisico} unidades."
            )

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
    list_display = ['nombre', 'precio', 'stockProducto', 'descripcion'] #Estos son los campos a mostrar en el administrador en la tabla
    list_filter = ['categoria'] # Estos son los campos de filtro
    search_fields = ['nombre'] # Estos son los campos de busqueda
    filter_horizontal = ['categoria', 'tallaDisponible', 'tipoMateria', 'instruccionesCuidado'] # Estos son los campos de filtro horizontal para que se pase la informacion de una tabla a otra
    inlines = [StockTallaInline, FotoProductoInline]  # Aqui agregamos la clase de StockTallaInline  y la clase de FotoProductoInline

    #Metodo para mostrar el stock de las tallas
    def stock_tallas(self, obj):
        return StockTalla.objects.filter(producto=obj).aggregate(
            total=Sum('talla_stock')
        )['total'] or 0
    stock_tallas.short_description = 'Stock Asignado'

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