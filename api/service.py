import json
from decimal import Decimal
from .models import Cliente, Resena, Pedido, DetallePedido, Producto, Talla, StockTalla
from django.contrib.auth.models import User
from django.db import transaction
import stripe
from django.conf import settings
from django.urls import reverse


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

                # Bloqueamos la fila de StockTalla con select_for_update() para evitar
                # condiciones de carrera si dos usuarios compran el mismo producto y talla
                # simultáneamente. Esto requiere que estemos dentro de transaction.atomic().
                stock_talla = StockTalla.objects.select_for_update().get(
                    producto=producto_obj, talla=talla
                )
                if stock_talla.talla_stock < cantidad:
                    raise ValueError(
                        f"Stock insuficiente para {producto_obj.nombre} "
                        f"(talla {talla.nombreTalla}): "
                        f"solicitado {cantidad}, disponible {stock_talla.talla_stock}"
                    )
                stock_talla.talla_stock -= cantidad
                stock_talla.save()

                precio = producto_obj.precio
                subtotal = precio * cantidad
                total += subtotal
                
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

class StripeService:

    """
    Servicio para la lógica de negocio relacionada con Stripe.

    SRP: Centraliza la integración con Stripe, facilitando cambios futuros
    (como cambiar a otro proveedor de pagos) sin afectar las vistas.
    """
    
    @staticmethod
    def obtener_o_crear_cliente(cliente: Cliente) -> str:
        """
        Verificar si el cliente de Django ya tiene un ID de Stripe asociado,
        Si no lo tiene, lo creamos en Stripe y lo guardamos en la base de datos.
        Devolvemos el ID de Stripe del cliente.
        """
        
        if cliente.stripe_customer_id:
            return cliente.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=cliente.usuario.email,
                name=cliente.usuario.username,
                metadata={
                    'django_user_id': cliente.usuario.id
                }
            )
            
        cliente.stripe_customer_id = customer.id
        cliente.save()
        return customer.id
        
    @staticmethod
    def crear_session_checkout(pedido: Pedido, request) -> str:
        """
        Crea una sesión de checkout de Stripe para un pedido.

        Args:
            pedido: Pedido para el cual se va a crear la sesión de pago.
            request: HttpRequest para construir URLs de éxito y cancelación.

        Retorna:
            URL de la sesión de checkout de Stripe.
        """        
        stripe.api_key = settings.STRIPE_SECRET_KEY # Obtenemos la clave secreta de Stripe desde las configuraciones de Django, esto es una buena práctica para no hardcodear claves en el código fuente
        stripe_customer_id = StripeService.obtener_o_crear_cliente(pedido.cliente)

        line_items = [] # Lista de items que se enviarán a Stripe, cada uno con su precio, cantidad y descripción. Esto se construye a partir de los detalles del pedido, transformando la información de nuestros modelos a lo que Stripe espera.
        for detalle in pedido.detalles.all():
            line_items.append({
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': detalle.producto.nombre,
                    },
                    'unit_amount': int(detalle.precio_unitario * 100), # Stripe espera el monto en centavos
                },
                'quantity': detalle.cantidad,
            })

        session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            line_items=line_items,
            billing_address_collection='required', # Requerimos la información de la dirección de facturación, por seguridad ayuda a evitar fraudes.
            
            # Para guardar el metodo de pago y la informacion de la tarjeta de crédito en la base de datos
            payment_intent_data={
                'setup_future_usage': 'on_session'
            },
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('pago_exitoso', args=[pedido.id])
            ) + '?session_id={CHECKOUT_SESSION_ID}', # Agregamos el session_id como query param para poder verificar el pago en la vista de éxito
            cancel_url=request.build_absolute_uri(
                reverse('checkout')
            ) + '?cancelado=1', # Agregamos un query param para identificar que el pago fue cancelado
        )
        
        pedido.stripe_id_sesion = session.id # Guardamos el ID de la sesión de Stripe en el pedido para futuras referencias (como verificar el estado del pago)
        pedido.save(update_fields=['stripe_id_sesion']) # Solo actualizamos el campo stripe_id_sesion para optimizar la consulta a la base de datos

        return session.url