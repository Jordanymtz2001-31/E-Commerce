import json
from decimal import Decimal
from .models import Cliente, Resena, Pedido, DetallePedido, Producto, Talla
from django.contrib.auth.models import User
from django.db import transaction


class ClienteService:
    """
    Servicio para la lógica de negocio relacionada con Cliente.

    SRP: Separamos la lógica de negocio (creación de User + Cliente en una
    transacción) de la capa de presentación (vistas) y de persistencia (modelos).
    DIP: Las vistas dependen de esta abstracción en vez de llamar directamente
    a Cliente.objects.create(), facilitando cambios futuros en la lógica.
    """

    @staticmethod
    def registrar(datos: dict) -> Cliente:
        """
        Crea un User y su Cliente asociado en una sola transacción atómica.

        Por qué transaction.atomic(): si falla la creación del Cliente después
        de haber creado el User, se revierte todo para evitar un User huérfano
        sin perfil de Cliente.
        """
        with transaction.atomic():
            user = User.objects.create_user(
                username=datos['username'],
                password=datos['password1'],
                email=datos['email']
            )

            return Cliente.objects.create(
                usuario=user,
                telefono=datos['telefono'],
                direccion=datos['direccion']
            )


class ResenaService:
    """
    Servicio para la lógica de negocio relacionada con Reseñas.

    SRP: Aísla la validación y creación de reseñas, manteniendo las vistas
    delgadas y facilitando el testing unitario sin HTTP.
    """

    @staticmethod
    def crear(producto, usuario, estrellas: int, comentario: str) -> Resena:
        if estrellas < 1 or estrellas > 5:
            raise ValueError("Las estrellas deben estar entre 1 y 5")

        return Resena.objects.create(
            producto=producto,
            usuario=usuario,
            estrellas=estrellas,
            comentario=comentario.strip()
        )


class PedidoService:
    """
    Servicio para la lógica de negocio relacionada con Pedidos.

    SRP: La creación de un pedido involucra varias operaciones (crear Pedido,
    crear DetallePedido, calcular total) que deben ser atómicas. Esto evita
    que la vista tenga que coordinar múltiples operaciones de base de datos.
    """

    @staticmethod
    def crear(cliente: Cliente, productos: list) -> Pedido:
        """
        Crea un Pedido con sus DetallePedido a partir de una lista de items.

        Args:
            cliente: Cliente que realiza el pedido.
            productos: Lista de dicts con {id: product_id, talla: str, cantidad: int}.

        La transacción asegura que si algo falla (producto no existe, talla
        inválida), no se quede un pedido a medio crear.
        """
        with transaction.atomic():
            total = Decimal('0.00') # Inicializamos el total del pedido en 0, lo iremos sumando a medida que procesamos cada item
            detalles_data = [] # Lista para almacenar los objetos DetallePedido que vamos a crear, esto nos permite usar bulk_create para optimizar la inserción en la base de datos

            for item in productos:
                producto_obj = Producto.objects.get(pk=item['id'])
                talla = Talla.objects.get(nombreTalla=item['talla'])
                cantidad = int(item['cantidad'])
                
                precio = producto_obj.precio
                subtotal = precio * cantidad
                total += subtotal
                
                # Agregamos el DetallePedido a la lista, pero sin asignarle el pedido aún, ya que necesitamos el ID del pedido para eso
                detalles_data.append(DetallePedido(
                    producto=producto_obj,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    Talla=talla,
                ))

            # Creamos el pedido con el total calculado, pero sin detalles aún, ya que necesitamos el ID del pedido para asignarlo a los detalles
            pedido = Pedido.objects.create(
                cliente=cliente,
                total=total,
            )

            # Por cada detalle en detalles_data
            for detalle in detalles_data:
                detalle.pedido = pedido # Asignamos el pedido al detalle antes de guardarlo en la base de datos
            DetallePedido.objects.bulk_create(detalles_data) # Guardamos los detalles en la base de datos

            return pedido
