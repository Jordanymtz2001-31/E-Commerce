from django.contrib import admin
from django.dispatch import receiver
from django.forms import BaseInlineFormSet, ValidationError
from django.db.models import Sum

# Regrsitramos nuestro modelos en el panel del administrador que puede ver los datos y realizar operaciones
from .models import InstruccionesCuidado, Producto, Categoria, Cliente, Resena, StockTalla, Talla, TipoMateria

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

class StockTallaInline(admin.TabularInline):
    model = StockTalla
    formset = StockTallaFormSet
    extra = 1  # Esto es para que se muestre un formulario extra
    fields = ['talla', 'talla_stock']  # Solo estos campos

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stockProducto', 'descripcion', 'imagen'] #Estos son los campos a mostrar en el administrador en la tabla
    list_filter = ['categoria'] # Estos son los campos de filtro
    search_fields = ['nombre'] # Estos son los campos de busqueda
    filter_horizontal = ['categoria', 'tallaDisponible', 'tipoMateria', 'instruccionesCuidado'] # Estos son los campos de filtro horizontal para que se pase la informacion de una tabla a otra
    inlines = [StockTallaInline]  # Aqui agregamos la clase de StockTallaInline 

    #Metodo para mostrar el stock de las tallas
    def stock_tallas(self, obj):
        return StockTalla.objects.filter(producto=obj).aggregate(
            total=Sum('talla_stock')
        )['total'] or 0
    stock_tallas.short_description = 'Stock Asignado'

"""
@admin.register(StockTalla)
class StockTallaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'talla', 'talla_stock']
    list_filter = ['producto', 'talla']

    #Creamos un metodo para validar el estock
    def stock_valido(self, obj):    
        ""Muestra si el stock es valido o no""
        try: 
            obj.clean()
            return "Valido"
        except ValidationError:
            return "Excede el stock disponible"
        
    stock_valido.short_description = "Stock"

    def save_model(self, request, obj, form, change):
        ""Valida ANTES de guardar""
        try:
            obj.full_clean() #Llama a clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Error: {str(e)}", level="error")
"""
@admin.register(Resena)
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'estrellas', 'comentario', 'fecha']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'direccion'] # Estos son los campos a mostrar en el administrador en la tabla
    search_fields = ['usuario']

