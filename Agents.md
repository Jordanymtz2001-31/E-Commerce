# Agents.md — Talcahualme E-commerce

## Descripción General

**Talcahualme** es un e-commerce de ropa artesanal mexicana construido con Django en arquitectura monolítica. Permite a visitantes explorar productos sin registrarse, y a usuarios registrados dejar reseñas. El administrador gestiona todo el contenido desde el panel de Django Admin personalizado con Jazzmin.

---

## Stack Tecnológico

- **Backend:** Django (Python) — arquitectura monolítica
- **Frontend:** Django Templates + Bootstrap 5.3 + Bootstrap Icons + Google Fonts (Plus Jakarta Sans)
- **Base de datos:** Configurable por entorno (SQLite en desarrollo, MySQL/PostgreSQL en producción)
- **Almacenamiento de archivos:** Local en desarrollo / Cloudflare R2 (S3-compatible) en producción
- **Archivos estáticos:** WhiteNoise con compresión
- **Panel admin:** Django Admin + Jazzmin (tema personalizado)
- **Despliegue:** Seenode (contenedor), variables de entorno por `.env.development` / `.env.production`

---

## Estructura del Proyecto

```
ecommerce/          → Configuración principal de Django (settings, urls, wsgi, asgi)
api/                → Única app Django con toda la lógica
  models.py         → Modelos de datos
  views.py          → Vistas (controladores)
  urls.py           → Rutas URL
  admin.py          → Configuración del panel de administración
  forms.py          → Formularios Django
  templates/        → Plantillas HTML
  static/           → CSS, JS e imágenes estáticas
  migrations/       → Migraciones de base de datos
media/              → Archivos subidos por el admin (imágenes de productos, eventos, colaboradores)
staticfiles/        → Archivos estáticos recolectados para producción
```

---

## Modelos de Datos

### `Categoria`
Clasifica los productos. Opciones fijas: `Niño`, `Adulto`, `Tradicional`, `Innovador`, `Algodon`, `Lana`.

### `Talla`
Tallas disponibles: `CH` (Chica), `M` (Mediana), `GR` (Grande), `UG` (Unitalla).

### `TipoMateria`
Material del producto: `Algodon` o `Lana`.

### `InstruccionesCuidado`
Instrucciones de lavado/cuidado del producto (texto libre).

### `Producto`
Entidad central del catálogo.
- Campos: `nombre`, `precio`, `descripcion`, `stockProducto`
- Relaciones M2M: `categoria`, `tallaDisponible`, `tipoMateria`, `instruccionesCuidado`
- Propiedades calculadas: `stock_disponible`, `tiene_stock`

### `ImagenProducto`
Imágenes asociadas a un producto (múltiples por producto). Subidas a `media/productos/`.

### `StockTalla`
Stock por combinación producto+talla. Al guardar, sincroniza automáticamente `tallaDisponible` del producto. Valida que el stock asignado por tallas no exceda el `stockProducto` total.

### `Resena`
Reseña de un cliente sobre un producto.
- Campos: `estrellas` (1–5), `comentario`, `fecha`
- Requiere usuario autenticado para crearse.
- Ordenadas por fecha descendente.

### `Cliente`
Extiende el `User` de Django con `telefono` y `direccion`. Relación 1:1 con `User`.

### `PuntoVenta`
Ubicaciones físicas donde se vende el producto.
- Campos: `nombre`, `ciudad`, `direccion`, `telefono`, `horario`, `maps_embed_url`, `maps_url`, `es_principal`, `activo`

### `Colaborador`
Marcas o personas que colaboran con Talcahualme.
- Campos: `nombre`, `descripcion`, `logo`, `url`

### `Evento`
Eventos pasados y próximos de la marca.
- Campos: `nombre`, `descripcion`, `fecha`, `lugar`, `activo`
- Relación M2M con `Colaborador`
- Propiedad calculada: `es_proximo` (compara con fecha actual)
- Ordenados por fecha descendente.

### `FotoEvento`
Fotos asociadas a un evento. Subidas a `media/eventos/`.

---

## Vistas y Rutas

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/` | `tienda_view` | Página principal "Nosotros" — acceso público |
| `/registro/` | `registro_view` | Formulario de registro de nuevo usuario |
| `/login/` | `login_view` | Inicio de sesión |
| `/logout/` | `logout_view` | Cierre de sesión, redirige a tienda |
| `/productList/` | `productos_view` | Catálogo de productos con filtro por categoría |
| `/producto/<pk>/resena/` | `crear_resena` | Crear reseña (requiere login) |
| `/punto_venta/` | `punto_venta_view` | Mapa y lista de puntos de venta activos |
| `/eventos/` | `eventos_view` | Eventos próximos y pasados |

---

## Flujos de Usuario

### Visitante (sin cuenta)
- Navega la página "Nosotros" con la historia de la marca.
- Explora el catálogo de productos, filtra por categoría.
- Ve el detalle de cada producto en un modal (imágenes, tallas, materiales, cuidados, stock).
- Consulta puntos de venta con mapa embebido de Google Maps.
- Consulta eventos próximos y pasados con fotos.
- Ve el mensaje "Inicia sesión para dejar tu reseña" en el modal de producto.

### Usuario Registrado
- Todo lo anterior, más:
- Deja reseñas con calificación de estrellas (1–5) y comentario en cualquier producto.
- Ve su nombre en el navbar ("¡Hola [usuario]!").
- Puede cerrar sesión.

### Registro de Usuario
- Formulario con: `username`, `email`, `password1`, `password2`, `telefono`, `direccion`.
- Al registrarse se crea automáticamente un `Cliente` vinculado al `User`.
- Redirige al login tras registro exitoso.

---

## Panel de Administración

Accesible en `/admin/`. Personalizado con **Jazzmin** (tema oscuro, logo de Talcahualme, navbar fijo).

### Entidades gestionables por el admin:

| Modelo | Capacidades |
|--------|-------------|
| `Producto` | CRUD completo. Filtro por categoría, búsqueda por nombre. Gestión inline de stock por talla y fotos del producto. Validación: stock por tallas no puede exceder stock físico total. |
| `Categoria` | CRUD. Lista de opciones predefinidas. |
| `Talla` | CRUD con búsqueda. |
| `TipoMateria` | CRUD. |
| `InstruccionesCuidado` | CRUD. |
| `StockTalla` | Gestionado inline desde `Producto`. |
| `ImagenProducto` | Gestionado inline desde `Producto` (múltiples imágenes). |
| `Resena` | Visualización y gestión de reseñas de clientes. |
| `Cliente` | Lista de clientes registrados con teléfono y dirección. Búsqueda por usuario. |
| `PuntoVenta` | CRUD. Filtro por activo/principal. Edición rápida del campo `activo` desde la lista. |
| `Colaborador` | CRUD con búsqueda por nombre. |
| `Evento` | CRUD. Filtro por activo/fecha. Gestión inline de fotos. Indicador visual de si el evento es próximo. Edición rápida del campo `activo`. |
| `FotoEvento` | Gestionado inline desde `Evento`. |

---

## Componentes Frontend Relevantes

### `base.html`
Plantilla base heredada por todas las páginas. Incluye:
- Navbar sticky con links de navegación y estado de sesión.
- Footer con categorías dinámicas, contacto y redes sociales.
- Modal global de detalle de producto (se llena con JS).
- Sistema de mensajes Django (alertas flotantes).
- Inyección de `window.USER_LOGGED_IN` para lógica JS de autenticación.

### `modal-producto.js`
Maneja el modal de detalle de producto:
- Llena dinámicamente título, precio, categorías, tallas, materiales, cuidados, stock y carrusel de imágenes.
- Muestra formulario de reseña si el usuario está logueado, o mensaje de login requerido si no.
- Construye la URL del formulario de reseña dinámicamente por producto.

### `carrito.js`
Archivo presente (funcionalidad de carrito — actualmente comentada en el modal, pendiente de implementación completa).

### `artesanal.css`
Estilos personalizados del sitio: chips de filtro, cards de producto, hero sections, footer artesanal, botones de navegación, modal de producto.

---

## Configuración de Entornos

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `True` en desarrollo, `False` en producción |
| `ALLOWED_HOSTS` | Hosts permitidos separados por coma |
| `DB_ENGINE` | Motor de base de datos |
| `DB_NAME` | Nombre de la base de datos |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Credenciales de BD |
| `DJANGO_PRODUCTION` | `1` para activar modo producción |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_ENDPOINT_URL`, `R2_PUBLIC_URL` | Credenciales de Cloudflare R2 (solo producción) |

---

## Notas de Arquitectura

- **Monolítica:** toda la lógica vive en la app `api`. No hay separación en microservicios ni API REST.
- **Sin carrito funcional:** el carrito está referenciado en el JS pero la funcionalidad está comentada en el template. Es una deuda técnica pendiente.
- **Sin sistema de pagos:** actualmente el e-commerce es un catálogo + vitrina. No hay checkout ni integración de pagos.
- **Autenticación nativa de Django:** se usa `django.contrib.auth` sin librerías externas (no hay JWT, no hay OAuth).
- **Imágenes en producción vía R2:** en desarrollo se sirven localmente desde `media/`.
- **Idioma:** configurado en `es-mx` (español México).
