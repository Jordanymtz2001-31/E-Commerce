# 📋 AUDITORÍA CSS - TALCAHUALME E-COMMERCE

**Fecha:** 2026-03-18  
**Archivo analizado:** `api/static/css/artesanal.css`  
**HTML analizados:** 5 archivos (base.html, tienda.html, productos.html, login.html, registro.html)

---

## 1. RESUMEN EJECUTIVO

| Métrica | Resultado |
|---------|-----------|
| **Tamaño CSS actual** | ~1880 líneas |
| **Clases CSS totales** | ~120+ definidas |
| **Clases realmente usadas** | ~85-90 |
| **CSS no utilizado** | ~15-20% |
| **Rutas/Pseudo-elementos no usados** | ~5-8% |
| **Duplicación de código** | Moderada (login/registro) |

---

## 2. CSS DEFINITIVAMENTE NO UTILIZADO

### 🔴 Alto impacto (Eliminar primero):

#### 2.1 Carrito/Compra (COMENTADO EN HTML)
```css
/* LÍNEAS: ~1065-1080 (estimado) */
.btn-cantidad
.cantidad-control
.btn-agregar-carrito
```
**Razón:** Seccionado con comentarios en base.html (<!--...-->)
**Recomendación:** ELIMINAR completamente
**Impacto:** ~15-20 líneas de CSS

#### 2.2 Badge "Nueva Colección" (versión antigua)
```css
/* LÍNEA: ~125 */
.badge-nueva-coleccion {
    max-width: 200px;
}
```
**Razón:** Nunca aparece en HTML. Se usa `.etiqueta-nueva` en su lugar
**Recomendación:** ELIMINAR
**Impacto:** ~3 líneas

#### 2.3 Estilos Login/Registro DUPLICADOS

El CSS contiene **2 juegos de estilos compete** para login y registro:

**Set 1 (antiguo - ~200 líneas):**
```css
.login-card (versión antigua card-based)
.register-hero (versión antigua)
.register-card (versión antigua card-based)
.input-group-register (versión antigua)
.form-label-register (variante antigua)
.form-control-register (variante 1)
```

**Set 2 (nuevo - ~150 líneas):**
```css
.login-wrapper (split screen)
.login-form-col
.login-form-inner
.login-titulo
.login-subtitulo
.login-footer
.registro-wrapper (split screen)
.registro-hero (versión optimizada)
.registro-form-col
.registro-form-inner
```

**HTML actual usa:** Set 2 (split screen layout)
**Impacto:** Eliminar Set 1, ~200 líneas de código muerto

---

## 3. ESTILOS PARCIALMENTE UTILIZADOS

### 🟡 Mediocre uso (Revisar):

#### 3.1 `.hero-dark`
```css
.hero-dark {
    background: linear-gradient(135deg, #221810 0%, #1a120b 100%);
}
```
✅ **Usado en:** `productos.html` (hero section)  
❌ **Potencial mejora:** No tiene responsividad, podría optimizarse

#### 3.2 `.material-symbols-outlined` (pseudo-selector)
```css
.material-symbols-outlined { ... }
```
✅ **Usado:** Ampliamente (iconos por todo el sitio)  
✅ **Está bien**

#### 3.3 `.btn-hover-scale` y `.card-hover-scale`
```css
.btn-hover-scale:hover, .card-hover-scale img:hover {
    transform: scale(1.05) !important;
}
```
❌ **Usado:** NO aparece en ningún HTML
**Recomendación:** ELIMINAR (es una clase obsoleta, se usa `.card-hover` en su lugar)

#### 3.4 Estilos de Input/Form antiguos no usados
```css
.form-label-login (línea ~870)  ❌ NO USADO
.form-control-login (línea ~876)  ❌ NO USADO
```
HTML actual usa clases Bootstrap estándares

---

## 4. CÓDIGO DUPLICADO/SOBRECARGADO

### 🔵 Instancias de duplicación:

#### 4.1 Pseudo-elementos `::before` excesivos
Encontrados en:
- `.btn-artesanal` 
- `.btn-explorar`
- `.btn-login` (x2 versiones)
- `.btn-nav*` (x4 botones)
- `.login-card`
- `.register-card`
- `.mision-card`
- `.titulo-hero`

**Patrón repetido:**
```css
/* Shine effect (aparece 8+ veces) */
::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.6s ease;
}
```
**Propuesta:** Crear clase `.shine-effect` reutilizable

#### 4.2 Gradientes repetidos
```css
/* Aparece 12+ veces */
background: linear-gradient(135deg, var(--primary), #f4a261)
background: linear-gradient(135deg, #ec6d13 0%, #f4a261 50%, #e76f51 100%)
```
**Propuesta:** Variables CSS:
```css
--gradient-primary: linear-gradient(135deg, var(--primary), #f4a261);
--gradient-primary-strong: linear-gradient(135deg, #ec6d13 0%, #f4a261 50%, #e76f51 100%);
```

#### 4.3 Shadow repetidos
```css
/* Aparece 8+ veces */
box-shadow: 0 10px 30px rgba(236,109,19,0.3);
box-shadow: 0 25px 50px -12px rgba(236,109,19,0.15);
```
**Propuesta:** Variables CSS para sombras

---

## 5. ESTILOS "ORFANDOS" (Nunca referenciados)

```css
/* Línea ~82 */
.btn-hover-scale:hover,
.card-hover-scale img:hover { }
→ ELIMINAR (clase nunca usada en HTML)

/* Línea ~90 */
.btn-outline-hover-primary:hover { }
→ ELIMINAR (nunca usado)

/* Línea ~100 */
.chips-scroll::-webkit-scrollbar { }
→ PUEDE ELIMINARSE (scroll es casi invisible en móvil)

/* Línea ~122-130 */
.badge-nueva-coleccion { }
→ ELIMINAR (obsoleto, se usa .etiqueta-nueva)

/* Línea ~145-155 */
.badge-position, .badge-top-right, .badge-top-left { }
→ REVISIÓN: Ver si se usan realmente (son estilos genéricos no específicos)
```

---

## 6. MEDIA QUERIES REDUNDANTES

**Problema:** Muchos media queries casi idénticos:

```css
/* Aparece en múltiples clases el mismo patrón */
@media (max-width: 768px) { ... }
@media (max-width: 576px) { ... }
@media (max-width: 480px) { ... }
```

Repetido en:
- `.btn-nav` × 2
- `.btn-nav-salir` × 2
- `.btn-nav-login` × 2
- `.btn-nav-registro` × 2
- `.span-precio` × 2
- `.modal-*` × 3
- `.badge` × 2
- `.timeline-*` × 1
- `.form-*` × 2

**Impacto:** ~150-200 líneas de código repetitivo

---

## 7. ANIMACIONES NO USADAS O DUPLICADAS

```css
@keyframes pulse { }          /* Línea ~305 - usado en 3 lugares */
@keyframes pulse-heart { }    /* Línea ~1387 - solo .mision-icon */
@keyframes float { }          /* Línea ~1312 - solo .badge-artesanal */
@keyframes slideUp { }        /* Línea ~890 - solo .login-card/.register-card */
@keyframes fadeIn { }         /* Línea ~660 - usado en filter animation */
@keyframes shake { }          /* Línea ~1665 - solo errores validación */
```

**análisis:** Todas se usan, están bien. ✅

---

## 8. LISTADO DE CLASES A ELIMINAR

| Clase | Línea (aprox) | Tipo | Razón |
|-------|---------------|------|-------|
| `.btn-cantidad` | 1070 | Selector compuesto | Comentado en HTML |
| `.cantidad-control` | 1065 | Selector compuesto | Comentado en HTML |
| `.btn-agregar-carrito` | 1080 | Selector compuesto | Comentado en HTML |
| `.badge-nueva-coleccion` | 125 | Propiedad | Reemplazado por `.etiqueta-nueva` |
| `.btn-hover-scale` | 85 | Selector | Nunca usado en HTML |
| `.card-hover-scale` | 85 | Selector | Nunca usado en HTML |
| `.btn-outline-hover-primary` | 100 | Selector | Nunca usado en HTML |
| `.badge-position` | 135 | Selector | Genérico, no usado |
| `.badge-top-right` | 136 | Selector | Genérico, no usado |
| `.badge-top-left` | 137 | Selector | Genérico, no usado |
| `.form-label-login` | 870 | Selector | Duplicado, HTML usa Bootstrap |
| `.form-control-login` | 876 | Selector | Duplicado, HTML usa Bootstrap |
| `.login-card` (version 1) | 895-975 | Bloque completo | DUPLICADO - usar Set 2 |
| `.register-hero` (version 1) | 980-1000 | Bloque | DUPLICADO - usar Set 2 |
| `.register-card` (version 1) | 887-975 | Bloque | DUPLICADO - usar Set 2 |

**Total a eliminar: ~300-350 líneas de CSS**

---

## 9. RECOMENDACIONES DE REFACTORIZACIÓN

### Opción A: Mantener un único archivo (NO recomendado para sitio pequeño)
✅ **Ventajas:**
- Menos requests HTTP
- Compilación simple

❌ **Desventajas:**
- 1880 líneas difíciles de mantener
- Difícil encontrar estilos específicos
- Responsabilidad única incumplida
- Difícil en equipo

---

### Opción B: Dividir en módulos CSS (RECOMENDADO) ⭐

**Estructura propuesta:**
```
api/static/css/
├── artesanal.css          (solo variables + imports, ~50 líneas)
├── base/
│   ├── _variables.css     (colores, gradientes, sombras, ~40 líneas)
│   ├── _reset.css         (html, body, reset, ~20 líneas)
│   ├── _typography.css    (fuentes, tamaños, ~30 líneas)
│   └── _animations.css    (keyframes, ~50 líneas)
├── components/
│   ├── _navbar.css        (navbar + botones nav, ~150 líneas)
│   ├── _buttons.css       (todos los botones, ~200 líneas)
│   ├── _modal.css         (modal producto, ~200 líneas)
│   ├── _cards.css         (card-hover, product cards, ~100 líneas)
│   └── _badges.css        (badges, etiquetas, ~80 líneas)
├── layout/
│   ├── _footer.css        (footer, ~100 líneas)
│   ├── _hero.css          (hero sections, ~120 líneas)
│   └── _timeline.css      (timeline, ~80 líneas)
├── pages/
│   ├── _login.css         (login solo split screen, ~150 líneas)
│   ├── _registro.css      (registro solo split screen, ~150 líneas)
│   └── _tienda.css        (tienda específico, ~80 líneas)
└── responsive/
    ├── _tablet.css        (media queries 768px-992px, ~150 líneas)
    ├── _mobile.css        (media queries 576px-768px, ~150 líneas)
    └── _mobile-small.css  (media queries <480px, ~100 líneas)
```

**Beneficios:**
- ✅ Organización clara
- ✅ Fácil de mantener
- ✅ Responsabilidad única
- ✅ Mejor para trabajo en equipo
- ✅ Más fácil debuggear
- ✅ Compilable a un único archivo para producción

---

## 10. PLAN DE ACCIÓN

### Fase 1: Limpieza inmediata (30 min)
**Tareas:**
1. ❌ Eliminar comentadas en HTML: `.btn-cantidad`, `.cantidad-control`, `.btn-agregar-carrito`
2. ❌ Eliminar obsoletas: `.badge-nueva-coleccion`
3. ❌ Eliminar nunca usadas: `.btn-hover-scale`, `.card-hover-scale`, `.btn-outline-hover-primary`
4. ❌ Eliminar Set 1 de Login/Registro (las versiones "card" antiguas)
5. ✅ Ejecutar: `py manage.py collectstatic --clear --noinput`

**Resultado:** Reducir de 1880 a ~1450-1500 líneas

---

### Fase 2: Parámetros CSS (15 min)
**Tareas:**
1. Crear variables para gradientes:
   ```css
   :root {
     --gradient-primary: linear-gradient(135deg, var(--primary), #f4a261);
     --shadow-elevation-1: 0 10px 30px rgba(236,109,19,0.3);
     --shadow-elevation-2: 0 25px 50px -12px rgba(236,109,19,0.15);
     --shine-effect: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
   }
   ```

**Resultado:** Reducir duplicación 30%

---

### Fase 3: Refactorización a módulos (2-3 horas)
**Tareas:**
1. Crear estructura de carpetas como Opción B
2. Migrar CSS por categoría
3. Crear archivo `artesanal.css` con imports:
   ```css
   @import 'base/_variables.css';
   @import 'base/_reset.css';
   @import 'base/_typography.css';
   @import 'base/_animations.css';
   @import 'components/_navbar.css';
   /* ... etc */
   ```
4. Verificar todo funciona
5. Ejecutar `collectstatic`

**Nota:** Django puede compilar automáticamente o usar herramienta como SASS (posterior)

---

## 11. HERRAMIENTAS SUGERIDAS (Fase 4)

Si quieres mejorar aún más:

### Para minificación:
```bash
# Instalar SASS/SCSS
npm install -D sass

# Compilar CSS
sass api/static/css/artesanal.scss api/static/css/artesanal.min.css --style=compressed
```

### Para identificar CSS no usado automáticamente:
```bash
# PurgeCSS (detecta clases no usadas)
npm install -D purgecss
```

### Para tests de accesibilidad y performance:
- Lighthouse (Chrome DevTools)
- axe DevTools

---

## 12. ESTIMACIÓN DE GANANCIA

| Métrica | Antes | Después (Fase 1+2) | Después (Fase 3) |
|---------|-------|-------------------|------------------|
| Líneas CSS | 1880 | 1350 | 1350 |
| Tamaño (minificado) | ~28KB | ~21KB | ~20KB |
| Mantenibilidad | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Tiempo búsqueda | 20 min | 10 min | 3 min |
| Código muerto | 15-20% | <5% | <5% |

---

## 13. PRÓXIMOS PASOS RECOMENDADOS

1. ✅ **Hoy:** Ejecutar Fase 1 (limpieza rápida)
2. ⏭️ **Próxima sesión:** Ejecutar Fase 2 (variables CSS)
3. 📅 **Futuro:** Fase 3 (modularización) cuando haya más tiempo

---

## Notas finales

Este proyecto **está bien estructurado** para un desarrollo inicial. El CSS monolítico es aceptable para equipos pequeños/individuales. La modularización (Fase 3) es un "nice-to-have", no urgencia.

**Mi recomendación:** Haz Fase 1 + Fase 2 ahora (45 min), y guarda Fase 3 para cuando tengas más tiempo o el proyecto crezca.

