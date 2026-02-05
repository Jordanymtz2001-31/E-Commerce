from django.contrib import admin

# Regrsitramos nuestro modelos en el panel del administrador que puede ver los datos y realizar operaciones
from .models import InstruccionesCuidado, Producto, Categoria, Cliente, Resena, StockTalla, Talla, TipoMateria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombreCategoria']

@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    list_display = ['nombreTalla']

@admin.register(TipoMateria)
class TipoMateriaAdmin(admin.ModelAdmin):
    list_display = ['nombreTipoMateria']

@admin.register(InstruccionesCuidado)
class InstruccionesCuidadoAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stockProducto', 'descripcion', 'imagen'] #Estos son los campos a mostrar en el administrador en la tabla
    list_filter = ['categoria'] # Estos son los campos de filtro
    search_fields = ['nombre'] # Estos son los campos de busqueda
    filter_horizontal = ['categoria', 'tallaDisponible', 'tipoMateria', 'instruccionesCuidado'] # Estos son los campos de filtro horizontal para que se pase la informacion de una tabla a otra
@admin.register(StockTalla)
class StockTallaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'talla', 'talla_stock']

@admin.register(Resena)
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'estrellas', 'comentario', 'fecha']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'direccion'] # Estos son los campos a mostrar en el administrador en la tabla
    search_fields = ['usuario']

