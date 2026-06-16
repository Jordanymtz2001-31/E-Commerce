"""
Tests unitarios para las vistas de la aplicación api.

Cada clase de TestCase representa un grupo de pruebas relacionadas con una vista específica.
El método setUp() se ejecuta antes de cada test para preparar los datos de prueba.

Para ejecutar los tests:
    python manage.py test api.tests --settings=ecommerce.test_settings
"""

from django.test import TestCase, Client
from django.urls import reverse #El reverse() se utiliza para obtener la URL de una vista basada en su nombre
from django.contrib.auth.models import User
from django.utils import timezone # Para trabajar con fechas
from api.models import Categoria, Producto, Cliente, Resena, PuntoVenta, Evento, Talla


# ============================================================================
# Tests para la vista principal (Tienda/Nosotros)
# ============================================================================
class TiendaViewTest(TestCase):
    """
    Pruebas para la vista de la tienda (página principal/nosotros).
    Verifica que la página carga correctamente y retorna los datos esperados.
    """
    
    def setUp(self):
        """
        Configuración inicial de cada test.
        Creamos un cliente de pruebas y una categoría para el contexto.
        """
        self.client = Client()  # Cliente simula el navegador
        Categoria.objects.create(nombreCategoria='Adulto')  # Datos de prueba

    def test_tienda_view_GET(self):
        """
        Test: La página principal carga correctamente.
        
        Qué hace:
        1. Simula una petición GET a la URL 'tienda'
        2. Verifica que responde con código 200 (éxito)
        3. Verifica que usa la plantilla 'tienda.html'
        4. Verifica que pasan las categorías al contexto
        """

        #La respuesta hace una petición GET a la URL 'tienda'
        response = self.client.get(reverse('tienda'))
        
        #Comprobaciones
        self.assertEqual(response.status_code, 200)  # La página existe
        self.assertTemplateUsed(response, 'tienda.html')  # Usa la plantilla correcta
        self.assertIn('categorias', response.context)  # Tiene las categorías


# ============================================================================
# Tests para el catálogo de productos
# ============================================================================
class ProductosViewTest(TestCase):
    """
    Pruebas para la vista del catálogo de productos.
    Verifica el listado de productos y los filtros por categoría.
    """
    
    def setUp(self):
        """
        Configuración: cliente, categoría y producto de prueba.
        """
        self.client = Client()
        self.categoria = Categoria.objects.create(nombreCategoria='Adulto')
        self.producto = Producto.objects.create(
            nombre='Test Product',
            precio=100.00,
            descripcion='Test description',
        )
        self.producto.categoria.add(self.categoria)

    def test_productos_view_GET(self):
        """
        Test: El catálogo de productos carga correctamente.
        
        Qué hace:
        1. Solicita la página del catálogo
        2. Verifica código 200
        3. Verifica plantilla 'productos.html'
        4. Verifica que hay productos en el contexto
        """

        #La respuesta hace una petición GET a la URL 'productList'
        response = self.client.get(reverse('productList'))
        
        #Comprobaciones
        self.assertEqual(response.status_code, 200) # La página existe
        self.assertTemplateUsed(response, 'productos.html') # Usa la plantilla correcta
        self.assertIn('productos', response.context) # Tiene los productos

    def test_productos_view_con_filtro(self):
        """
        Test: El filtro por categoría funciona correctamente.
        
        Qué hace:
        1. Solicita productos con filtro de categoría en la URL
        2. Verifica que la categoría seleccionada está en el contexto
        """
        #La respuesta hace una petición GET a la URL 'productList' con el filtro de categoría
        response = self.client.get(f"{reverse('productList')}?categoria={self.categoria.id}")
        
        #Comprobaciones
        self.assertEqual(response.status_code, 200) # La página existe
        self.assertEqual(response.context['categoria_seleccionada'], self.categoria) # La categoría seleccionada es la correcta

    def test_productos_view_sin_filtro(self):
        """
        Test: Sin filtro, no hay categoría seleccionada.
        
        Qué hace:
        1. Solicita productos sin filtro
        2. Verifica que categoria_seleccionada es None
        """
        response = self.client.get(reverse('productList'))
        
        self.assertEqual(response.status_code, 200) # La página existe
        self.assertIsNone(response.context['categoria_seleccionada']) # No hay categoría seleccionada


# ============================================================================
# Tests para autenticación (login/logout)
# ============================================================================
class AutenticacionViewTest(TestCase):
    """
    Pruebas para las vistas de autenticación: login y logout.
    Verifica el funcionamiento correcto del inicio y cierre de sesión.
    """
    
    def setUp(self):
        """
        Configuración: cliente y usuario de prueba.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_exitoso(self):
        """
        Test: Login con credenciales correctas redirige a la tienda.
        
        Qué hace:
        1. Envía POST con username y password válidos
        2. Verifica que redirige (código 302)
        3. Verifica que la redirección va a 'tienda'
        """

        #La respuesta hace una petición POST a la URL 'login' con los datos de prueba
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        #Comprobaciones
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertRedirects(response, reverse('tienda'))  # Va a tienda

    def test_login_fallido(self):
        """
        Test: Login con contraseña incorrecta muestra error.
        
        Qué hace:
        1. Envía POST con password incorrecta
        2. Verifica que vuelve a mostrar el formulario (código 200)
        """

        #La respuesta hace una petición POST a la URL 'login' con los datos de prueba incorrectos
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        self.assertEqual(response.status_code, 200)  # No redirecciona

    def test_login_GET(self):
        """
        Test: La página de login carga correctamente.
        
        Qué hace:
        1. Solicita la página de login (GET)
        2. Verifica código 200 y plantilla correcta
        """

        #La respuesta hace una petición GET a la URL 'login'
        response = self.client.get(reverse('login'))
        
        #Comprobaciones
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_logout(self):
        """
        Test: El cierre de sesión redirige a la tienda.
        
        Qué hace:
        1. Simula que el usuario ha iniciado sesión
        2. Solicita la URL de logout
        3. Verifica redirección a 'tienda'
        """

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        
        self.assertEqual(response.status_code, 302) # Verifica redirección
        self.assertRedirects(response, reverse('tienda')) # Va a tienda una ves cerrada la sesion


# ============================================================================
# Tests para el registro de usuarios
# ============================================================================
class RegistroViewTest(TestCase):
    """
    Pruebas para la vista de registro de nuevos usuarios.
    Verifica el formulario y la creación de usuarios y clientes.
    """
    
    def setUp(self):
        """
        Configuración: solo el cliente de pruebas.
        """
        self.client = Client()

    def test_registro_GET(self):
        """
        Test: La página de registro carga con el formulario.
        
        Qué hace:
        1. Solicita la página de registro
        2. Verifica que carga correctamente
        3. Verifica que tiene el formulario en el contexto
        """
        response = self.client.get(reverse('registro'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registro.html') # Usa la plantilla correcta
        self.assertIn('form', response.context) # Tiene el formulario

    def test_registro_exitoso(self):
        """
        Test: Registro con datos válidos crea usuario y cliente.
        
        Qué hace:
        1. Envía POST con todos los datos requeridos
        2. Verifica redirección al login
        3. Verifica que el usuario fue creado en la base de datos
        4. Verifica que también se creó el registro de Cliente
        """
        response = self.client.post(reverse('registro'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'telefono': '1234567890',
            'direccion': 'Test Address'
        })
        
        #Comprobaciones
        self.assertEqual(response.status_code, 302) # verifica la redirección
        self.assertRedirects(response, reverse('login')) # Va al login
        self.assertTrue(User.objects.filter(username='newuser').exists()) # Existe el usuario
        self.assertTrue(Cliente.objects.filter(usuario__username='newuser').exists()) # Existe el cliente

    def test_registro_passwords_diferentes(self):
        """
        Test: Registro falla si las contraseñas no coinciden.
        
        Qué hace:
        1. Envía POST con passwords diferentes
        2. Verifica que NO se crea el usuario
        3. Verifica que el formulario se vuelve a mostrar (código 200)
        """
        response = self.client.post(reverse('registro'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'newpass123',
            'password2': 'differentpass',
            'telefono': '1234567890',
            'direccion': 'Test Address'
        })
        
        self.assertEqual(response.status_code, 200) # No redirecciona
        self.assertFalse(User.objects.filter(username='newuser').exists()) # No existe el usuario 


# ============================================================================
# Tests para crear reseñas de productos
# ============================================================================
class ResenaViewTest(TestCase):
    """
    Pruebas para la vista de creación de reseñas.
    Verifica que solo usuarios autenticados pueden crear reseñas.
    """
    
    def setUp(self):
        """
        Configuración: cliente, usuario, cliente, categoría y producto.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            telefono='1234567890',
            direccion='Test Address'
        )
        self.categoria = Categoria.objects.create(nombreCategoria='Adulto')
        self.producto = Producto.objects.create(
            nombre='Test Product',
            precio=100.00,
            descripcion='Test',
        )
        self.producto.categoria.add(self.categoria)

    def test_crear_resena_sin_login(self):
        """
        Test: Usuario sin login es redirigido al login.
        
        Qué hace:
        1. Intenta crear reseña sin estar autenticado
        2. Verifica que se redirige al login
        """
        response = self.client.post(
            reverse('crear_resena', args=[self.producto.pk]),
            {'estrellas': 5, 'comentario': 'Great!'}
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url) # Redirige al login

    def test_crear_resena_con_login(self):
        """
        Test: Usuario logueado puede crear una reseña.
        
        Qué hace:
        1. Simula login del usuario
        2. Envía datos de la reseña
        3. Verifica que la reseña se creó en la base de datos
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('crear_resena', args=[self.producto.pk]),
            {'estrellas': 5, 'comentario': 'Great product!'}
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Resena.objects.filter(producto=self.producto, usuario=self.cliente).exists())

    def test_crear_resena_estrellas_invalidas(self):
        """
        Test: Reseña con estrellas fuera de rango (1-5) se maneja correctamente.
        
       Qué hace:
        1. Envía estrellas con valor 10 (inválido)
        2. Verifica que la petición es procesada
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('crear_resena', args=[self.producto.pk]),
            {'estrellas': 10, 'comentario': 'Test'}
        )
        
        self.assertEqual(response.status_code, 302) 


# ============================================================================
# Tests para puntos de venta
# ============================================================================
class PuntoVentaViewTest(TestCase):
    """
    Pruebas para la vista de puntos de venta.
    Verifica que solo se muestran los puntos activos.
    """
    
    def setUp(self):
        """
        Configuración: cliente y categoría.
        """
        self.client = Client()
        Categoria.objects.create(nombreCategoria='Adulto')

    def test_punto_venta_view(self):
        """
        Test: La página de puntos de venta carga correctamente.
        
        Qué hace:
        1. Crea un punto de venta activo
        2. Solicita la página
        3. Verifica que el punto de venta está en el contexto
        """
        PuntoVenta.objects.create(
            nombre='Tienda Test',
            ciudad='Mexico',
            direccion='Calle 123',
            telefono='1234567890',
            activo=True
        )
        
        response = self.client.get(reverse('punto_venta'))
        
        self.assertEqual(response.status_code, 200) # No redirecciona
        self.assertTemplateUsed(response, 'puntos_venta.html') # Usa la plantilla correcta
        self.assertIn('puntos_venta', response.context) # Hay puntos de venta en el contexto

    def test_punto_venta_solo_activos(self):
        """
        Test: Solo se muestran los puntos de venta activos.
        
        Qué hace:
        1. Crea un punto activo y uno inactivo
        2. Solicita la página
        3. Verifica que solo el activo aparece en el contexto
        """
        PuntoVenta.objects.create(
            nombre='Tienda Activa',
            ciudad='Mexico',
            telefono='1234567890',
            activo=True
        )
        PuntoVenta.objects.create(
            nombre='Tienda Inactiva',
            ciudad='Guadalajara',
            telefono='1234567890',
            activo=False
        )
        
        response = self.client.get(reverse('punto_venta'))
        
        self.assertEqual(response.status_code, 200) # No redirecciona
        self.assertEqual(len(response.context['puntos_venta']), 1)  # Solo 1 activo


# ============================================================================
# Tests para eventos
# ============================================================================
class EventosViewTest(TestCase):
    """
    Pruebas para la vista de eventos.
    Verifica que se separan eventos próximos y pasados.
    """
    
    def setUp(self):
        """
        Configuración: cliente y categoría.
        """
        self.client = Client()
        self.categoria = Categoria.objects.create(nombreCategoria='Adulto')

    def test_eventos_view(self):
        """
        Test: La página de eventos carga con eventos próximos y pasados.
        
        Qué hace:
        1. Crea un evento
        2. Solicita la página
        3. Verifica que tanto 'proximos' como 'pasados' están en el contexto
        """
        Evento.objects.create(
            nombre='Test Event',
            descripcion='Test description',
            lugar='Test Place',
            fecha=timezone.now().date(),
            activo=True
        )
        
        response = self.client.get(reverse('eventos'))
        
        self.assertEqual(response.status_code, 200) # No redirecciona
        self.assertTemplateUsed(response, 'eventos.html') # Usa la plantilla correcta
        self.assertIn('proximos', response.context) # Hay proximos en el contexto
        self.assertIn('pasados', response.context) # Hay pasados en el contexto

    def test_eventos_solo_activos(self):
        """
        Test: Solo se muestran los eventos activos.
        
        Qué hace:
        1. Crea un evento activo y uno inactivo
        2. Verifica que solo el activo existe en la base de datos
        """
        Evento.objects.create(
            nombre='Evento Activo',
            lugar='Test',
            fecha=timezone.now().date(),
            activo=True
        )
        Evento.objects.create(
            nombre='Evento Inactivo',
            lugar='Test',
            fecha=timezone.now().date(),
            activo=False
        )
        
        response = self.client.get(reverse('eventos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Evento.objects.filter(activo=True).count(), 1)


# ============================================================================
# Tests para productos filtrados por categoría
# ============================================================================
class ProductosPorCategoriaViewTest(TestCase):
    """
    Pruebas para la vista de productos por categoría específica.
    Verifica el funcionamiento del filtro y el manejo de errores.
    """
    
    def setUp(self):
        """
        Configuración: cliente, categoría y producto.
        """
        self.client = Client()
        self.categoria = Categoria.objects.create(nombreCategoria='Adulto')
        self.producto = Producto.objects.create(
            nombre='Test Product',
            precio=100.00,
            descripcion='Test',
        )
        self.producto.categoria.add(self.categoria)

    def test_productos_por_categoria(self):
        """
        Test: Los productos se filtran correctamente por categoría.
        
        Qué hace:
        1. Solicita la URL con el ID de categoría
        2. Verifica que carga correctamente
        3. Verifica que la categoría seleccionada está en el contexto
        """
        response = self.client.get(reverse('productos_por_categoria', args=[self.categoria.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos.html')
        self.assertEqual(response.context['categoria_seleccionada'], self.categoria)

    def test_categoria_inexistente(self):
        """
        Test: Solicitar una categoría que no existe devuelve 404.
        
        Qué hace:
        1. Solicita un ID de categoría que no existe (9999)
        2. Verifica que devuelve error 404 (Página no encontrada)
        """
        response = self.client.get(reverse('productos_por_categoria', args=[9999]))
        
        self.assertEqual(response.status_code, 404)