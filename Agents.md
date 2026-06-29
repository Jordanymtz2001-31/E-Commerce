# Agents.md — Talcahualme E-commerce

## Descripción General

Talcahualme es un e-commerce de ropa artesanal mexicana construido con Django en arquitectura monolítica. Visitantes exploran productos; usuarios registrados dejan reseñas y compran. El admin gestiona todo desde Django Admin + Jazzmin.

**Stack:** Django + Django Templates + Bootstrap 5.3 + Bootstrap Icons + Material Symbols + Google Fonts. BD: configurable (SQLite/MySQL/PostgreSQL). Archivos: local o Cloudflare R2. Estáticos: WhiteNoise. Pagos: Stripe (Checkout Sessions). Despliegue: Seenode.

---

## Skills Requeridas

Antes de cualquier tarea creativa (features, componentes, funcionalidad), carga los skills en este orden:

1. **$Braixnstorming** — para explorar requerimientos, diseño e intención antes de implementar.
2. **$Django-expert** — para todo lo relacionado con modelos, vistas, ORM, migraciones, DRF, servicios, repositorios.
3. **$Interface-design** — para diseño de dashboards, paneles admin, apps e interfaces interactivas.
4. **$Stripe-* (4 skills)** — para pagos, connected accounts, facturación y aprovisionamiento:
   - `$Stripe-best-practices` — elegir API, configurar Connect, suscripciones, seguridad.
   - `$Stripe-directory` — buscar socios, proveedores o servicios.
   - `$Stripe-projects` — aprovisionar infraestructura (DBs, hosting, LLMs).
   - `$Upgrade-stripe` — migrar versiones de API/SDK.

---

## Comportamiento del Agente

- **Haz preguntas** cuando algo no esté claro: requerimientos ambiguos, decisiones de diseño, preferencias.
- No asumas convenciones externas sin verificar primero el código existente.
- Sigue las convenciones del proyecto (estilo, patrones, estructura, librerías ya usadas).
- Verifica siempre con lint/tests cuando sea aplicable.

---

## Stack y Estructura

```
ecommerce/              → Configuración Django (settings, urls, wsgi, asgi)
api/                    → Única app con toda la lógica
  models.py             → 15 modelos de datos
  views.py              → Vistas (14 rutas)
  urls.py               → Rutas URL
  admin.py              → Panel admin (Jazzmin)
  forms.py              → Formularios Django
  service.py            → Capa de servicios (Cliente, Resena, Pedido, Stripe)
  repositories.py       → Capa de repositorios (Producto, Categoria, PuntoVenta, Evento, Pedido)
  strategies.py         → Estrategias de filtrado (Strategy Pattern)
  validators.py         → Validadores personalizados
  tests.py              → Tests (554 líneas)
  templates/            → 10 plantillas HTML
  static/               → CSS, JS e imágenes
  migrations/           → 12 migraciones
media/                  → Archivos subidos por el admin
staticfiles/            → Estáticos recolectados para producción
```

---

## Modelos de Datos (15)

| Modelo | Tabla | Propósito |
|--------|-------|-----------|
| `Categoria` | `categorias` | Clasifica productos (Niño, Adulto, Tradicional, Innovador, Algodon, Lana) — `nombreCategoria` unique |
| `Talla` | `tallas` | Tallas: CH, M, GR, UG |
| `TipoMateria` | `tipos_materia` | Material: Algodon, Lana |
| `InstruccionesCuidado` | `instrucciones_cuidado` | Instrucciones de lavado/cuidado (texto libre) |
| `Color` | `colores` | Color con código hex. M2M en Producto |
| `Producto` | `productos` | Catálogo central. M2M: categoria, tallaDisponible, tipoMateria, instruccionesCuidado, color. Props: `stock_disponible`, `tiene_stock` |
| `ImagenProducto` | `imagenes_productos` | Múltiples imágenes por producto. Inline en admin |
| `StockTalla` | `stock_tallas` | Stock por producto+talla. Signal: sincroniza `tallaDisponible`. Unique together. Validación contra stock total |
| `Resena` | `resenas` | 1-5 estrellas + comentario. Requiere login. Orden: fecha descendente |
| `Cliente` | `clientes` | 1:1 con User. Campos: telefono, direccion, stripe_customer_id |
| `Pedido` | `pedidos` | FK cliente, estado (PENDIENTE/PAGADO/FALLIDO/ENVIADO), total, stripe_id_sesion |
| `DetallePedido` | `detalles_pedido` | FK pedido, FK producto (PROTECT), cantidad, precio_unitario, FK Talla (PROTECT) |
| `PuntoVenta` | `puntos_venta` | Ubicaciones físicas con Google Maps embed |
| `Colaborador` | `colaboradores` | Marcas/colaboradores con logo |
| `Evento` | `eventos` | Eventos con propiedad `es_proximo`. M2M colaboradores. Fotos inline |
| `FotoEvento` | `fotos_eventos` | Fotos de eventos |

---

## Vistas y Rutas (14 rutas)

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/` | `tienda_view` | Página principal "Nosotros" |
| `/registro/`, `/login/`, `/logout/` | auth views | Registro, inicio/cierre de sesión |
| `/productList/` | `productos_view` | Catálogo con filtro por categoría y color |
| `/categoria/<int:categoria_id>/` | `productos_por_categoria` | Productos filtrados por categoría vía URL |
| `/producto/<pk>/resena/` | `crear_resena` | Crear reseña (requiere login) |
| `/punto_venta/` | `punto_venta_view` | Puntos de venta con mapa |
| `/eventos/` | `eventos_view` | Eventos próximos y pasados |
| `/checkout/` | `checkout_view` | Checkout con Stripe. GET: formulario. POST: crea pedido + redirect a Stripe |
| `/pedido/<pk>/pago-exitoso/` | `pago_exitoso_view` | Confirmación de pago vía Stripe |
| `/pedido/<pk>/confirmacion/` | `pedido_confirmado_view` | Detalle del pedido confirmado |
| `/stripe/webhook/` | `stripe_webhook_view` | Webhook Stripe (sin CSRF). Maneja `checkout.session.completed` y `expired` |
| `/mis-pedidos/` | `mis_pedidos_view` | Lista de pedidos del usuario autenticado |

---

## Flujo de Compra (Carrito + Stripe)

1. **Cliente** explora productos y hace clic en "Ver Detalles"
2. **Modal** muestra imágenes, tallas (radio buttons), cantidad, y botón "Agregar al canasto"
3. **`carrito.js`** gestiona el carrito en `localStorage` (clave `carrito`) usando `obtenerKey(productoId, talla)`
4. **Offcanvas** se renderiza automáticamente: items, total, botón "Proceder al pago"
5. **Checkout** (`checkout.html`) — resume carrito desde localStorage, datos de envío del cliente. Si `STRIPE_ENABLED = False`, muestra advertencia beta
6. **POST a `/checkout/`** — `PedidoService.crear()` valida stock con `select_for_update()`, crea Pedido + DetallePedido en transacción atómica, calcula total
7. **Stripe Checkout Session** — `StripeService.crear_session_checkout()` crea sesión con line items en MXN, guarda `stripe_id_sesion` en Pedido
8. **Redirect a Stripe** — usuario paga en checkout.stripe.com
9. **`/pedido/<pk>/pago-exitoso/`** — verifica `session.payment_status == 'paid'`, actualiza estado a PAGADO
10. **Webhook** — `stripe_webhook_view` maneja `checkout.session.completed` y `expired` como respaldo
11. **Cancelación** — si el usuario cancela, `PedidoService.restaurar_stock()` devuelve stock, estado = FALLIDO

---

## Panel de Administración

Accesible en `/admin/`. Personalizado con Jazzmin (tema oscuro, logo Talcahualme, sidebar fijo, navbar fijo, temas Bootswatch configurables).

**14 modelos registrados** con `@admin.register`. Características destacadas:
- **ProductoAdmin**: list_display con `stock_tallas()` (Sum agregado), filter_horizontal en M2M, inlines de StockTalla e ImagenProducto
- **StockTallaInline**: fields (talla, talla_stock) con FormSet personalizado
- **PuntoVentaAdmin**: `list_editable` para campo `activo`, filtros por activo/es_principal
- **EventoAdmin**: indicador visual `es_proximo` como boolean, filter_horizontal para colaboradores, inline FotoEvento
- **ColorAdmin**: `mostrar_color()` — renderiza swatch de color inline en la lista

---

## Capa de Servicios

| Servicio | Métodos | Descripción |
|----------|---------|-------------|
| `ClienteService` | `registrar()` | Crea User + Cliente en transacción atómica |
| `ResenaService` | `crear()` | Valida estrellas (1-5), crea reseña |
| `PedidoService` | `crear()`, `restaurar_stock()` | Transacciones atómicas con `select_for_update()`, `bulk_create()`, restaura stock en fallos |
| `StripeService` | `obtener_o_crear_cliente()`, `crear_session_checkout()` | Gestión de customer IDs en Stripe, creación de Checkout Sessions con line items |

## Capa de Repositorios

| Repositorio | Métodos clave |
|-------------|---------------|
| `ProductoRepository` | `listar_con_stock()`, `listar_con_desglose_tallas()`, `filtrar_por_categoria()`, `obtener_por_categoria()` |
| `CategoriaRepository` | `listar_todas()` |
| `PuntoVentaRepository` | `listar_activos()` |
| `EventoRepository` | `listar_proximos()` (asc), `listar_pasados()` (desc, con prefetch) |
| `PedidoRepository` | `listar_por_cliente()` (evita N+1 con Prefetch + select_related), `obtener_con_detalles()` |

## Patrones de Diseño

- **Strategy Pattern** en `strategies.py`: `FiltroProductoStrategy` (ABC), `SinFiltro` (null object), `FiltroPorCategoria`, `FiltroPorColor`
- **Service Layer**: desacopla lógica de negocio de las vistas
- **Repository Pattern**: abstrae acceso a datos y consultas complejas
- **Signals**: `sincronizar_talla_disponible` en post_save de StockTalla

---

## Componentes Frontend

**10 templates**, todas heredan de `base.html`:

- **`base.html`** (351 líneas): Navbar sticky con logo, categorías, icono carrito con badge, auth. Footer con categorías dinámicas, contacto, redes. Offcanvas carrito. Toast de notificación. Modal de producto global. Incluye Bootstrap 5.3, Google Fonts (Plus Jakarta Sans), Material Symbols, Bootstrap Icons.

- **`productos.html`**: Hero section, chips de filtro por categoría/color, grid de productos con data-attributes para modal.

- **`checkout.html`**: Resumen del carrito desde localStorage, dirección de envío, advertencia Stripe, formulario POST con `cart_data`.

- **`pedido_confirmado.html`**: Confirmación con flag `pago_exitoso`, detalles, limpia localStorage.

- **`mis_pedidos.html`**: Lista de pedidos con badges de estado (PENDIENTE=warning, PAGADO=success, FALLIDO=danger, ENVIADO=info).

**JS**: `carrito.js` (203 líneas, gestión localStorage + offcanvas), `modal-producto.js` (303 líneas, modal + carrusel + selector tallas + agregar al carrito).

**CSS**: `artesanal.css` (1616 líneas — variables, navbar, cards, modal, footer, offcanvas, responsive), `admin_custom.css`.

---

## Configuración de Entornos

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | True/False según entorno |
| `ALLOWED_HOSTS` | Hosts permitidos separados por coma |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Configuración de BD |
| `DJANGO_PRODUCTION` | `1` para modo producción |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_ENDPOINT_URL`, `R2_PUBLIC_URL` | Cloudflare R2 (solo producción) |
| `STRIPE_ENABLED` | `True`/`False` — habilita pagos |
| `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Credenciales Stripe |

---

## Notas de Arquitectura

- **Monolítica**: toda la lógica en `api/`. Sin REST API ni microservicios.
- **Pagos integrados**: Stripe Checkout Sessions con webhook, manejo de cancelación y restauración de stock.
- **Carrito funcional**: 100% client-side via `localStorage`. Backend solo en checkout.
- **Auth nativa Django**: sin JWT, OAuth ni librerías externas.
- **Patrones**: Service Layer, Repository, Strategy, Signals.
- **Tests**: 554 líneas en `api/tests.py`.
- **Idioma**: `es-mx`, timezone UTC.
