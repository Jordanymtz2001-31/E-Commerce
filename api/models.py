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

#Creamos el modelo para las tallas, ya que un producto tiene varias tallas
class Talla(models.Model):
    TALLA = [
        ('CH', 'Chica'),
        ('M', 'Mediana'),
        ('GR', 'Grande'),
        ('UG', 'Unitalla')
    ]

    nombreTalla = models.CharField(max_length=50, choices=TALLA, unique=True)

    def __str__(self):
        return self.nombreTalla
    
#Creamos un modelo para el Tipo de Materia, ya que un producto puede ser de Algodon o Lana
class TipoMateria(models.Model):
    TIPO_MATERIA = [
        ('Algodon', 'Algodon'),
        ('Lana', 'Lana'),
    ]
    nombreTipoMateria = models.CharField(max_length=50, choices=TIPO_MATERIA, unique=True)

    def __str__(self):
        return self.nombreTipoMateria
    
#Creamos un modelo para las instrucciones de Cuida del Producto
class InstruccionesCuidado(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    nombre = models.CharField(max_length=50, null=False, blank=False) #Decimos que no puede estar vacio
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False) # Colocamos la cantidad de digitos y decimales

    # Un producto puede tener varias Categorias
    categoria = models.ManyToManyField(Categoria, related_name='productos') # Con related_name le decimos que se llame productos
    # Un producto puede tener varias Tallas
    tallaDisponible = models.ManyToManyField(Talla)
    # Un producto puede tener varias Tipos de Materia
    tipoMateria = models.ManyToManyField(TipoMateria)
    # Un producto puede tener varias Instrucciones de Cuida
    instruccionesCuidado = models.ManyToManyField(InstruccionesCuidado, blank=True) # Decimos que puede estar vacio

    stockProducto = models.IntegerField(default=0) # Por defecto el stock es 0
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='productos') # Ponermos la ruta donde se guardaran las imagenes

    #Metodo para obtener el stock disponible, en donde se suma el stock de todas las tallas 
    @property
    def stock_disponible(self):
        return sum(stock.talla_stock for stock in self.stocktalla_set.all())
    
    #Metodo para que nos diga si tiene stock
    @property
    def tiene_stock(self):
        return self.stock_disponible > 0

    def __str__(self):
        return self.nombre
#Creamos un modelo para el Stock de las tallas disponibles
class StockTalla(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE) # Le pasamos la llave foranea de Producto para que se relacionen
    talla = models.ForeignKey(Talla, on_delete=models.CASCADE) # Le pasamos la llave foranea de Talla para que se relacionen
    talla_stock = models.IntegerField(default=0) # Por defecto el stock es 0

    class Meta: # Aqui decimos que la combinacion de producto y talla debe ser unica, ya que sino hay dos productos con el mismo nombre y con otra talla, pero el nombre se repite
        unique_together = ('producto', 'talla') #Aqui decimos que la combinacion de producto y talla debe ser unica

    def __str__(self):
        return f"{self.producto} - {self.talla}" # Aqui decimos que se muestre el producto y la talla
    
#Creamos el modelo para las reseñas
class Resena(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey('Cliente', on_delete=models.CASCADE) # Le pasamos la llave foranea de Cliente para que se relacionen
    estrellas = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5) # Estrellas de 1 a 5
    comentario = models.TextField(blank=True) # Decimos que puede estar vacio
    fecha = models.DateTimeField(auto_now_add=True) # Colocamos la fecha y hora actual

    class Meta: # Cada vez que obtengas un queryset de Resena, por defecto vendrá ordenado por fecha descendente (de la más nueva a la más antigua)
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.producto} - {self.usuario}"

#Creamos el modelo para el cliente
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

    def __str__(self):
        return str(self.usuario.username)
