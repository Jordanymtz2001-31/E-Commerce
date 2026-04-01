# PRD - Talcahualme E-commerce

## 1. Descripción del Proyecto

**Talcahualme** es un e-commerce de ropa artesanal mexicana construido con Django en arquitectura monolítica. Permite a visitantes explorar productos sin registrarse, y a usuarios registrados dejar reseñas. El administrador gestiona todo el contenido desde el panel de Django Admin personalizado con Jazzmin.

## 2. Stack Tecnológico

- **Backend:** Django (Python) — arquitectura monolítica
- **Frontend:** Django Templates + Bootstrap 5.3 + Bootstrap Icons + Google Fonts (Plus Jakarta Sans)
- **Base de datos:** Configurable por entorno (SQLite en desarrollo, MySQL/PostgreSQL en producción)
- **Almacenamiento de archivos:** Local en desarrollo / Cloudflare R2 (S3-compatible) en producción
- **Archivos estáticos:** WhiteNoise con compresión
- **Panel admin:** Django Admin + Jazzmin (tema personalizado)
- **Despliegue:** Seenode (contenedor), variables de entorno por `.env.development` / `.env.production`

## 3. URLs de la Aplicación

**IMPORTANTE:** Todas las URLs de la aplicación tienen el prefijo `/talcahualme/`. Por ejemplo, `/registro/` en realidad es `/talcahualme/registro/`.

Las siguientes son las rutas disponibles en la aplicación:

| URL | Descripción |
|-----|-------------|
| `/talcahualme/` | Página principal "Nosotros" — acceso público |
| `/talcahualme/registro/` | Formulario de registro de nuevo usuario |
| `/talcahualme/login/` | Inicio de sesión |
| `/talcahualme/logout/` | Cierre de sesión, redirige a tienda |
| `/talcahualme/productList/` | Catálogo de productos con filtro por categoría |
| `/talcahualme/categoria/<id>/` | Productos filtrados por categoría |
| `/talcahualme/producto/<pk>/resena/` | Crear reseña (requiere login) |
| `/talcahualme/punto_venta/` | Mapa y lista de puntos de venta activos |
| `/talcahualme/eventos/` | Eventos próximos y passés |

## 4. Características Principales

### 4.1. Autenticación de Usuarios

- **Registro:** Los usuarios pueden registrarse con username, email, password, teléfono y dirección.
- **Login:** Los usuarios pueden iniciar sesión con username y password.
- **Logout:** Los usuarios pueden cerrar sesión.
- **Cliente:** Al registrarse se crea automáticamente un `Cliente` vinculado al `User`.

### 4.2. Catálogo de Productos

- Los visitantes pueden explorar el catálogo de productos.
- Los productos tienen categorías, tallas, materiales, instrucciones de cuidado y stock.
- Los usuarios pueden filtrar productos por categoría.

### 4.3. Reseñas

- Los usuarios registrados pueden dejar reseñas en los productos.
- Las reseñas tienen calificación de estrellas (1-5) y comentario.
- Las reseñas se muestran en el modal de detalle del producto.

### 4.4. Puntos de Venta

- Los usuarios pueden ver los puntos de venta activos en un mapa embebido de Google Maps.
- Los puntos de venta incluyen nombre, ciudad, dirección, teléfono, horario y enlace a Google Maps.

### 4.5. Eventos

- Los usuarios pueden ver los eventos próximos y pasados de la marca.
- Los eventos incluyen nombre, descripción, fecha, lugar y fotos.

## 5. Requisitos para TestSprite

### 5.1. Dependencias Requeridas

Para que TestSprite pueda ejecutar las pruebas correctamente, es necesario instalar las siguientes dependencias en el entorno de ejecución de las pruebas:

```bash
pip install beautifulsoup4 requests
```

- **beautifulsoup4 (bs4):** Se utiliza para analizar el HTML de las páginas y extraer información de él.
- **requests:** Se utiliza para realizar las peticiones HTTP a la aplicación.

### 5.2. URLs a Testear

TestSprite debe testear las siguientes URLs (todas con prefijo `/talcahualme/`):

- **GET `/talcahualme/`**: Verificar que la página principal carga correctamente.
- **GET `/talcahualme/login/`**: Verificar que la página de login carga correctamente.
- **GET `/talcahualme/registro/`**: Verificar que la página de registro carga correctamente.
- **POST `/talcahualme/registro/`**: Verificar que el registro de usuarios funciona correctamente.
  - **Caso exitoso:** Verificar que al enviar datos válidos, se redirige al usuario a la página de login.
  - **Caso fallido (contraseñas no coinciden):** Verificar que al enviar contraseñas que no coinciden, se muestra un mensaje de error.
- **POST `/talcahualme/login/`**: Verificar que el login de usuarios funciona correctamente.
  - **Caso exitoso:** Verificar que al iniciar sesión correctamente, se redirige al usuario a la página principal.
  - **Caso fallido (credenciales inválidas):** Verificar que al iniciar sesión con credenciales inválidas, se muestra un mensaje de error.
- **GET `/talcahualme/productList/`**: Verificar que el catálogo de productos carga correctamente.
- **GET `/talcahualme/categoria/<id>/`**: Verificar que el filtro de productos por categoría funciona correctamente.
- **POST `/talcahualme/producto/<pk>/resena/`**: Verificar que la creación de reseñas funciona correctamente (requiere login).
- **GET `/talcahualme/punto_venta/`**: Verificar que la página de puntos de venta carga correctamente.
- **GET `/talcahualme/eventos/`**: Verificar que la página de eventos carga correctamente.

### 5.3. Consideraciones Adicionales

- **CSRF Token:** Al realizar peticiones POST, es necesario incluir el token CSRF de Django en las cabeceras de la petición. Este token se puede obtener del formulario de la página.
- **Sesiones:** Las pruebas que requieren autenticación deben mantener una sesión activa entre peticiones.
- **Redirecciones:** Algunas pruebas deben verificar que las redirecciones funcionan correctamente.
- **Mensajes de error:** Algunas pruebas deben verificar que los mensajes de error se muestran correctamente.

## 6. Modelo de Datos

Los modelos de datos principales son:

- **Categoria:** Clasifica los productos.
- **Talla:** Tallas disponibles.
- **TipoMateria:** Material del producto.
- **InstruccionesCuidado:** Instrucciones de lavado/cuidado.
- **Producto:** Entidad central del catálogo.
- **ImagenProducto:** Imágenes asociadas a un producto.
- **StockTalla:** Stock por combinación producto+talla.
- **Resena:** Reseña de un cliente sobre un producto.
- **Cliente:** Extiende el User de Django.
- **PuntoVenta:** Ubicaciones físicas donde se vende el producto.
- **Colaborador:** Marcas o personas que colaboran.
- **Evento:** Eventos de la marca.
- **FotoEvento:** Fotos asociadas a un evento.

## 7. Notas de Arquitectura

- **Monolítica:** Toda la lógica vive en la app `api`. No hay separación en microservicios ni API REST.
- **Sin carrito funcional:** El carrito está referenciado en el JS pero la funcionalidad está comentada.
- **Sin sistema de pagos:** Actualmente el e-commerce es un catálogo + vitrina.
- **Autenticación nativa de Django:** Se usa `django.contrib.auth` sin librerías externas.
- **Imágenes en producción vía R2:** En desarrollo se sirven localmente desde `media/`.
- **Idioma:** Configurado en `es-mx` (español México).
