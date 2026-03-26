from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


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

    class Meta:
        db_table = 'categorias'

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
    
    class Meta:
        db_table = 'tallas'
    
#Creamos un modelo para el Tipo de Materia, ya que un producto puede ser de Algodon o Lana
class TipoMateria(models.Model):
    TIPO_MATERIA = [
        ('Algodon', 'Algodon'),
        ('Lana', 'Lana'),
    ]
    nombreTipoMateria = models.CharField(max_length=50, choices=TIPO_MATERIA, unique=True)

    def __str__(self):
        return self.nombreTipoMateria
    
    class Meta:
        db_table = 'tipos_materia'

#Creamos un modelo para las instrucciones de Cuida del Producto
class InstruccionesCuidado(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'instrucciones_cuidado'
    
class Producto(models.Model):
    nombre = models.CharField(max_length=50, null=False, blank=False) #Decimos que no puede estar vacio
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False) # Colocamos la cantidad de digitos y decimales

    # Un producto puede tener varias Categorias
    categoria = models.ManyToManyField(Categoria, related_name='productos') # Con related_name le decimos que se llame productos
    # Un producto puede tener varias Tallas
    tallaDisponible = models.ManyToManyField(Talla, related_name='productos')
    # Un producto puede tener varias Tipos de Materia
    tipoMateria = models.ManyToManyField(TipoMateria, related_name='productos')
    # Un producto puede tener varias Instrucciones de Cuida
    instruccionesCuidado = models.ManyToManyField(InstruccionesCuidado, related_name='productos', blank=True) # Decimos que puede estar vacio

    stockProducto = models.IntegerField(default=0) # Por defecto el stock es 0
    descripcion = models.TextField()

    #Metodo para obtener el stock disponible, en donde se suma el stock de todas las tallas 
    @property
    def stock_disponible(self):
        total_stock = self.stocktalla_set.aggregate(total=models.Sum('talla_stock'))['total']
        return total_stock if total_stock else 0
    
    #Metodo para que nos diga si tiene stock
    @property
    def tiene_stock(self):
        return self.stock_disponible > 0

    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'productos'

#Creamos una clase para las imagenes de los productos
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes') # Le pasamos la llave foranea de Producto para que se relacionen
    imagenes = models.ImageField(upload_to='productos/', null=True, blank=True)

    class Meta:
        db_table = 'imagenes_productos'
        
#Creamos un modelo para el Stock de las tallas disponibles
class StockTalla(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE) # Le pasamos la llave foranea de Producto para que se relacionen
    talla = models.ForeignKey(Talla, on_delete=models.CASCADE) # Le pasamos la llave foranea de Talla para que se relacionen
    talla_stock = models.IntegerField(default=0) # Por defecto el stock es 0

    class Meta: # Aqui decimos que la combinacion de producto y talla debe ser unica, ya que sino hay dos productos con el mismo nombre y con otra talla, pero el nombre se repite
        unique_together = ('producto', 'talla') #Aqui decimos que la combinacion de producto y talla debe ser unica
        db_table = 'stock_tallas'

    def __str__(self):
        return f"{self.producto.nombre} - {self.talla.nombreTalla}"

    #Metodo para que cada ves que guarde StockTalla, se agregue la talla al producto
    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
            # Si tiene stock, agregar talla a tallaDisponible
            if self.talla_stock > 0:
                self.producto.tallaDisponible.add(self.talla)
            else:
                # Si ya no tiene stock, puedes decidir si la quitas:
                # self.producto.tallaDisponible.remove(self.talla)
                pass

#Creamos el modelo para las reseñas
class Resena(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey('Cliente', on_delete=models.CASCADE) # Le pasamos la llave foranea de Cliente para que se relacionen
    estrellas = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5) # Estrellas de 1 a 5
    comentario = models.TextField(blank=True) # Decimos que puede estar vacio
    fecha = models.DateTimeField(auto_now_add=True) # Colocamos la fecha y hora actual

    class Meta: # Cada vez que obtengas un queryset de Resena, por defecto vendrá ordenado por fecha descendente (de la más nueva a la más antigua)
        ordering = ['-fecha']
        db_table = 'resenas'

    def __str__(self):
        return f"{self.producto} - {self.usuario}"

#Creamos el modelo para el cliente ----------------------------------------------------------------------------------------------------
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

    def __str__(self):
        return str(self.usuario.username)

    class Meta:
        db_table = 'clientes'

#Modelo de Puntos de Venta ----------------------------------------------------------------------------------------------------------
class PuntoVenta(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20, blank=True)
    horario = models.CharField(max_length=100, blank=True)
    maps_embed_url = models.TextField(
        help_text="URL del iframe de Google Maps. Ve a maps.google.com → Compartir → Insertar mapa → copia solo el src del iframe"
    )
    maps_url = models.URLField(
        help_text="URL directa de Google Maps para el botón 'Ver en Google Maps'",
        blank=True
    )
    es_principal = models.BooleanField(default=False, help_text="Marcar si es el punto de venta principal")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"

    class Meta:
        db_table = 'puntos_venta'

#Modelo de Colaboradores ------------------------------------------------------------------------------------------------------------
class Colaborador(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    logo = models.ImageField(upload_to='colaboradores/', blank=True, null=True) #El upload_to es para guardar la imagen en la carpeta 'colaboradores/'
    url = models.URLField(blank=True, help_text="Sitio web o red social del colaborador")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'colaboradores'


class Evento(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha = models.DateField()
    lugar = models.CharField(max_length=200)
    colaboradores = models.ManyToManyField(Colaborador, blank=True, related_name='eventos') #El realated_name es para que se pueda acceder a los colaboradores de un evento
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.fecha}"

    @property
    def es_proximo(self):
        # Verificar si la fecha del evento es mayor o igual que la fecha actual        
        from django.utils import timezone
        return self.fecha >= timezone.now().date()

    class Meta:
        db_table = 'eventos'
        ordering = ['-fecha'] # Ordenar los eventos por fecha descendente


class FotoEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='fotos') #El related_name es para que se pueda acceder a las fotos de un evento
    foto = models.ImageField(upload_to='eventos/') #El upload_to es para guardar la imagen en la carpeta 'eventos/'
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Foto de {self.evento.nombre}"

    class Meta:
        db_table = 'fotos_eventos'