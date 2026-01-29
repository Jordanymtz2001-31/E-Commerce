from django.contrib import admin

# Regrsitramos nuestro modelos en el panel del administrador que puede ver los datos y realizar operaciones
from .models import Producto, Categoria, Cliente

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'categoria', 'descripcion', 'imagen'] #Estos son los campos a mostrar en el administrador en la tabla
    list_filter = ['categoria'] # Estos son los campos de filtro
    search_fields = ['nombre'] # Estos son los campos de busqueda

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombreCategoria']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'direccion'] # Estos son los campos a mostrar en el administrador en la tabla
    search_fields = ['usuario']

