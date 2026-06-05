# Agents.md — Talcahualme E-commerce

## Descripción General

Talcahualme es un e-commerce de ropa artesanal mexicana construido con Django en arquitectura monolítica. Visitantes exploran productos sin registrarse; usuarios registrados dejan reseñas. El admin gestiona todo desde Django Admin + Jazzmin.

**Stack:** Django + Django Templates + Bootstrap 5.3 + Bootstrap Icons + Google Fonts. BD: configurable (SQLite/MySQL/PostgreSQL). Archivos: local o Cloudflare R2. Estáticos: WhiteNoise. Despliegue: Seenode.

---

## Skills Requeridas

Antes de cualquier tarea creativa (features, componentes, funcionalidad), carga los skills en este orden:

1. **$Brainstorming** — para explorar requerimientos, diseño e intención antes de implementar.
2. **$Django-expert** — para todo lo relacionado con modelos, vistas, serializers, ORM, migraciones, DRF.
3. **$Interface-design** — para diseño de dashboards, paneles admin, apps e interfaces interactivas (no marketing).

---

## Comportamiento del Agente

- **Haz preguntas** cuando algo no esté claro: requerimientos ambiguos, decisiones de diseño, preferencias de implementación.
- No asumas convenciones externas sin verificar primero el código existente.
- Sigue las convenciones del proyecto (estilo de código, estructura, librerías ya usadas).
- Verifica siempre con lint/tests cuando sea aplicable.

---

## Stack y Estructura

```
ecommerce/          → Configuración Django (settings, urls, wsgi, asgi)
api/                → Única app con toda la lógica (models, views, urls, admin, forms, templates, static, migrations)
media/              → Subidas por el admin (productos, eventos, colaboradores)
staticfiles/        → Estáticos recolectados para producción
```

---

## Modelos Clave

`Categoria`, `Talla`, `TipoMateria`, `InstruccionesCuidado`, `Producto` (catálogo central, M2M con categoria/talla/materia/cuidados, propiedades `stock_disponible` y `tiene_stock`), `ImagenProducto` (inline en producto), `StockTalla` (valida que no exceda stock total), `Resena` (1-5 estrellas, requiere login), `Cliente` (1:1 con User), `PuntoVenta`, `Colaborador`, `Evento` (con `es_proximo`), `FotoEvento`.

---

## Vistas y Rutas Principales

| URL | Descripción |
|-----|-------------|
| `/` | Página principal "Nosotros" |
| `/registro/`, `/login/`, `/logout/` | Autenticación |
| `/productList/` | Catálogo con filtro por categoría |
| `/producto/<pk>/resena/` | Crear reseña (requiere login) |
| `/punto_venta/` | Puntos de venta con mapa |
| `/eventos/` | Eventos próximos y pasados |

---

## Notas de Arquitectura

- **Monolítica:** toda la lógica en `api/`. Sin REST API ni microservicios.
- **Sin carrito funcional:** JS presente pero comentado en templates (deuda técnica).
- **Sin pagos:** catálogo/vitrina, sin checkout ni integración de pagos.
- **Auth nativa Django:** sin JWT, OAuth ni librerías externas.
- **Idioma:** `es-mx`.
