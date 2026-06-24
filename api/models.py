from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from .validators import validar_tamano_imagen


class Categoria(models.Model):
    nombreCategoria = models.CharField(max_length=50, unique=True)

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
        
#Creamos el modelo para los colores---------------------------------------------------------------------------------------------------
class Color(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Nombre del color")
    codigo_hex = models.CharField(max_length=7, unique=True, help_text="Código hexadecimal del color, ej: #FF0000 (rojo)")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'colores'


class Producto(models.Model):
    nombre = models.CharField(max_length=50, null=False, blank=False)
    categoria = models.ManyToManyField(Categoria, related_name='productos')
    tipoMateria = models.ManyToManyField(TipoMateria, related_name='productos')
    instruccionesCuidado = models.ManyToManyField(InstruccionesCuidado, related_name='productos', blank=True)
    descripcion = models.TextField()

    @property
    def stock_disponible(self):
        """
        Retorna el stock total sumando todas las tallas.
        Si el queryset usó annotate(stock_total=Sum(...)) desde el repositorio,
        usa ese valor anotado (0 consultas SQL). Si no, hace aggregate (1 consulta).
        """
        if hasattr(self, 'stock_total') and self.stock_total is not None:
            return self.stock_total
        total = self.variantes.filter(activo=True).aggregate(total=Sum('stock'))['total']
        return total if total else 0
    
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
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagenes = models.ImageField(upload_to='productos/', null=True, blank=True, validators=[validar_tamano_imagen])

    class Meta:
        db_table = 'imagenes_productos'


class VarianteProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    talla = models.ForeignKey(Talla, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='variantes/', null=True, blank=True, validators=[validar_tamano_imagen])
    sku = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('producto', 'color', 'talla')
        db_table = 'variantes_producto'
        verbose_name = 'Variante de producto'
        verbose_name_plural = 'Variantes de producto'

    # Metodo para que nos diga el nombre de la variante convinando el producto, color y talla
    def __str__(self):
        partes = [self.producto.nombre]
        if self.color:
            partes.append(str(self.color))
        if self.talla:
            partes.append(str(self.talla))
        return ' - '.join(partes)

    def save(self, *args, **kwargs):
        # Si no se proporciona un SKU, genera uno basado en el producto, color y talla
        # Usamos replace() para reemplazar espacios en blanco con guiones bajos
        
        # Pero si ya tenemos un SKU lo mantenemos
        if not self.sku:
            color_part = self.color.nombre.upper().replace(' ', '_') if self.color else 'SIN_COLOR'
            talla_part = self.talla.nombreTalla.upper().replace(' ', '_') if self.talla else 'SIN_TALLA'
            self.sku = f"{self.producto.id}-{color_part}-{talla_part}"
            
            # Normalizamos el SKU para eliminar caracteres no deseados
            import unicodedata
            self.sku = unicodedata.normalize('NFKD', self.sku).encode('ASCII', 'ignore').decode('ASCII')

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        
        # Si la variante tiene una imagen, la borramos tambien
        if self.imagen:
            self.imagen.delete(save=False) # save=False para que no se guarde en la base de datos
        
        # Llamamos al metodo delete de la superclase
        super().delete(*args, **kwargs)


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
    
    # Campo clave para conectar con Stripe, puede ser nulo porque se crea el pedido antes de iniciar el proceso de pago
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True) 
    

    def __str__(self):
        return str(self.usuario.username)

    class Meta:
        db_table = 'clientes'
        
#Creamos el modelo de Pedido ------------------------------------------------------------------------------------------------------
class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADO', 'Pagado'),
        ('FALLIDO', 'Pago Fallido'),
        ('ENVIADO', 'Enviado'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    creado = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    # Campo clave para conectar con Stripe, puede ser nulo porque se crea el pedido antes de iniciar el proceso de pago
    stripe_id_sesion = models.CharField(max_length=255, blank=True, null=True) 
    
    class Meta:
        db_table = 'pedidos'
    
#Creamos el modelo de Detalle de Pedido (Tabla intermedia entre Pedido y Producto)------------------------------------------------------------------------------------------------------
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles') # El related_name es para que se pueda acceder a los detalles de un pedido
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Usamos PROTECT para evitar que se borre un producto que está en un pedido
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    talla = models.ForeignKey(Talla, on_delete=models.PROTECT)
    variante = models.ForeignKey(
        VarianteProducto, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='detalles_pedido'
    )

    class Meta:
        db_table = 'detalles_pedido'
        
#Modelo de Puntos de Venta ----------------------------------------------------------------------------------------------------------
class PuntoVenta(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20, blank=True)
    horario = models.CharField(max_length=100, blank=True)
    maps_embed_url = models.TextField(
        help_text="URL del iframe de Google Maps. Ve a maps.google.com \u2192 Compartir \u2192 Insertar mapa \u2192 copia solo el src del iframe"
    )
    maps_url = models.URLField(
        help_text="URL directa de Google Maps para el bot\u00f3n 'Ver en Google Maps'",
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
    logo = models.ImageField(upload_to='colaboradores/', blank=True, null=True, validators=[validar_tamano_imagen]) #El upload_to es para guardar la imagen en la carpeta 'colaboradores/'
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
    foto = models.ImageField(upload_to='eventos/', validators=[validar_tamano_imagen]) #El upload_to es para guardar la imagen en la carpeta 'eventos/'
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Foto de {self.evento.nombre}"

    class Meta:
        db_table = 'fotos_eventos'
