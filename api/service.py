import json
from decimal import Decimal
from .models import Cliente, Resena, Pedido, DetallePedido, Producto, Talla, VarianteProducto
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
            productos: Lista de dicts con {id, talla, cantidad, sku?, color?}.
            Cada item debe incluir sku de la VarianteProducto.

        ---
        Optimización N+1:
        La versión anterior hacía 3 consultas por cada item del carrito
        (Producto.get, Talla.get, VarianteProducto.select_for_update().get).
        Con 10 items en el carrito, eso era 30 consultas a MySQL.

        En un servidor Gunicorn con 4 workers, si 3 usuarios hacen checkout
        simultáneo, los 4 workers quedan atrapados esperando ~90 consultas
        mientras los requests de imágenes, CSS, etc. se encolan hasta que
        Gunicorn cierra la conexión (ERR_CONNECTION_CLOSED).

        Solución: Extraer todos los IDs/skus ANTES del for, hacer 3 consultas
        masivas con filter(__in=...), mapear a diccionarios en memoria y
        dentro del for solo acceder al dict — 0 consultas adicionales.

        select_for_update() también se hace en lote para bloquear todas las
        variantes involucradas en una sola transacción atómica, evitando
        deadlocks entre workers concurrentes.
        """
        with transaction.atomic():
            # --- FASE 1: Recopilar todos los IDs y skus ---
            producto_ids = [item['id'] for item in productos]
            tallas = [item['talla'] for item in productos]
            skus = [item['sku'] for item in productos]

            # --- FASE 2: Cargar todo en 3 consultas masivas ---
            # Creamos diccionarios en memoria con los IDs/skus/tallas de los items
            
            productos_map = {
                p.id: p # Claves : valores
                for p in Producto.objects.filter(pk__in=producto_ids) # pk__in indica que si esta dentro de la lista
            }
            tallas_map = {
                t.nombreTalla: t # Claves : valores
                for t in Talla.objects.filter(nombreTalla__in=set(tallas)) # nombreTalla__in indica que si esta dentro de la lista
            }
            
            # Traemos las variantes y las bloqueamos para evitar compras duplicadas simultáneas
            variantes = VarianteProducto.objects.filter(
                sku__in=skus, activo=True # Filtramos las variantes activas y las que estan en la lista de skus
            ).select_for_update()
            
            variantes_map = {
                v.sku: v  # Claves : valores
                for v in variantes
            }

            # --- FASE 3: Procesar items en memoria (0 consultas) ---
            total = Decimal('0.00')
            detalles_data = []
            variantes_a_actualizar = [] # Lista para guardar las variantes modificadas

            for item in productos:
                
                # Ahora accedemos directamente a los diccionarios en memoria
                producto_obj = productos_map.get(item['id'])
                if producto_obj is None:
                    raise Producto.DoesNotExist(
                        f"Producto con ID {item['id']} no encontrado."
                    )
                talla_obj = tallas_map.get(item['talla'])
                if talla_obj is None:
                    raise Talla.DoesNotExist(
                        f"Talla '{item['talla']}' no válida."
                    )
                cantidad = int(item['cantidad'])

                sku = item.get('sku')
                if not sku:
                    raise ValueError("El item del carrito no tiene SKU de variante.")

                variante_obj = variantes_map.get(sku)
                if variante_obj is None:
                    raise ValueError(
                        f"Variante con SKU {sku} no encontrada o inactiva."
                    )
                if variante_obj.stock < cantidad:
                    raise ValueError(
                        f"Stock insuficiente para {producto_obj.nombre} "
                        f"(variante {sku}): "
                        f"solicitado {cantidad}, disponible {variante_obj.stock}"
                    )
                    
                # Restamos stock en memoria
                variante_obj.stock -= cantidad
                if variante_obj not in variantes_a_actualizar:
                    variantes_a_actualizar.append(variante_obj)
                

                precio = variante_obj.precio
                subtotal = precio * cantidad
                total += subtotal

                detalles_data.append(DetallePedido(
                    producto=producto_obj,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    talla=talla_obj,
                    variante=variante_obj,
                ))

            # --- FASE 4: Crear pedido y guardar detalles ---
            pedido = Pedido.objects.create(
                cliente=cliente,
                total=total,
            )
            
            # Actualizamos el stock de todas las variantes afectadas
            if variantes_a_actualizar:
                VarianteProducto.objects.bulk_update(variantes_a_actualizar, ['stock']) # Con bulk_update hacemos 1 sola consultas

            # Asignamos el pedido creado a los detalles en memoria de forma limpia
            for detalle in detalles_data:
                detalle.pedido = pedido # Asignamos el pedido al detalle antes de guardarlo en la base de datos
            DetallePedido.objects.bulk_create(detalles_data) # Guardamos los detalles en la base de datos

            return pedido

    @staticmethod
    def restaurar_stock(pedido: Pedido) -> Pedido:
        """
        Restaura el stock de un pedido que no fue pagado (cancelado o expirado).

        ---
        Optimización N+1:
        La versión anterior iteraba sobre cada detalle y hacía un
        select_for_update().get() individual (N queries para N detalles).
        Ahora cargamos todas las variantes en un solo query con
        filter(pk__in=variante_ids).select_for_update() y las mapeamos
        en un diccionario para restaurar en memoria.
        """
        with transaction.atomic():
            
            # Cargamos los detalles y sus variantes asociadas
            detalles = pedido.detalles.select_related('variante').all()
            variante_ids = [d.variante_id for d in detalles if d.variante_id]
            
            # Bloqueamos las filas en la base de datos con select_for_update()
            variantes_map = {
                v.id: v # Claves : valores
                for v in VarianteProducto.objects.filter(
                    pk__in=variante_ids # pk__in indica que si esta dentro de la lista
                ).select_for_update()
            }
            
            variantes_a_actualizar = []
            
            # Modificamos el stock puramente en la memoria RAM
            for detalle in detalles:
                if detalle.variante_id and detalle.variante_id in variantes_map:
                    variante = variantes_map[detalle.variante_id]
                    variante.stock += detalle.cantidad
                    
                    if variante not in variantes_a_actualizar:
                        variantes_a_actualizar.append(variante)
                        
            # Enviamos una única consulta SQL para actualizar todas las variantes afectadas       
            if variantes_a_actualizar:
                VarianteProducto.objects.bulk_update(variantes_a_actualizar, ['stock'])
            
            # Actualizamos el estado del pedido
            pedido.estado = 'FALLIDO'
            pedido.save(update_fields=['estado'])
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
        
        # 1. Autenticación con Stripe utilizando las buenas prácticas
        stripe.api_key = settings.STRIPE_SECRET_KEY # Obtenemos la clave secreta de Stripe desde las configuraciones de Django, esto es una buena práctica para no hardcodear claves en el código fuente
        stripe_customer_id = StripeService.obtener_o_crear_cliente(pedido.cliente)

        # Optimización N+1: Usamos select_related('producto') para cargar
        # el nombre del producto en la misma consulta que los detalles.
        # Sin esto, cada acceso a detalle.producto.nombre dispararía una
        # consulta adicional (N queries para N detalles), saturando los
        # workers de Gunicorn igual que el checkout.
        
        # 2. Optimización N+1: Cargamos los detalles y sus productos base eficientemente
        detalles = pedido.detalles.select_related('producto').all()
        line_items = []
        
        for detalle in detalles:
            
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
            ) + f'?cancelado=1&pedido_id={pedido.id}', # Agregamos query params para identificar que el pago fue cancelado y restaurar el stock
        )
        
        pedido.stripe_id_sesion = session.id # Guardamos el ID de la sesión de Stripe en el pedido para futuras referencias (como verificar el estado del pago)
        pedido.save(update_fields=['stripe_id_sesion']) # Solo actualizamos el campo stripe_id_sesion para optimizar la consulta a la base de datos

        return session.url