from django.db import models
from django.db import models
from django.contrib.auth.models import User

#Creamos nuestros modelos

class Categoria(models.Model):
    CATEGORIA = [
        ('Niño', 'Niño'),
        ('Adulto', 'Adulto'),
        ('Tradicional', 'Tradicional'),
        ('Innovador', 'Innovador'),
        ('Algodon', 'Algodon'),
        ('Lana', 'Lana'),]
    nombreCategoria = models.CharField(max_length=50, choices=CATEGORIA)

    def __str__(self):
        return self.nombreCategoria
    
class Producto(models.Model):
    nombre = models.CharField(max_length=50, null=False, blank=False) #Decimos que no puede estar vacio
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False) # Colocamos la cantidad de digitos y decimales
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    stock = models.IntegerField()
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='productos')

    def __str__(self):
        return self.nombre
    
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

    def __str__(self):
        return str(self.usuario.username)
