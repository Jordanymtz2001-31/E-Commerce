/**
 * ============================================================================
 * slideshow.js — Slideshow interactivo en cards del catálogo
 * ============================================================================
 *
 * RESPONSABILIDAD:
 *   Cuando el usuario pasa el mouse sobre una card del catálogo que tiene
 *   más de una imagen general (ImagenProducto), este script cicla entre
 *   ellas con crossfade suave. Al salir, vuelve a la primera imagen.
 *   En móviles no hay hover → el slideshow nunca se activa.
 *
 * FLUJO:
 *   1. Busca todos los .producto-card-slideshow en el DOM
 *   2. Para cada uno cuenta las <img> hijas
 *   3. Si hay 2+ imágenes:
 *      - mouseenter → inicia setInterval cada 2.5s alternando .img-active
 *      - mouseleave → detiene y muestra la primera imagen
 *
 * DEPENDENCIAS:
 *   - Ninguna (JS puro, sin librerías externas)
 *
 * ESTRUCTURA HTML ESPERADA:
 *   .producto-card-slideshow         — contenedor con position:relative
 *     img.card-img-top               — todas las imágenes apiladas
 *     img.img-active                 — la imagen visible actualmente (opacity:1)
 *
 * TEMPLATE (productos.html):
 *   {% for img in producto.imagenes.all %}
 *   <img src="{{ img.imagenes.url }}" class="card-img-top ... {% if forloop.first %}img-active{% endif %}" ...>
 *   {% endfor %}
 */

document.addEventListener('DOMContentLoaded', function () {
    var slideshows = document.querySelectorAll('.producto-card-slideshow');

    slideshows.forEach(function (container) {
        var images = container.querySelectorAll('img');
        if (images.length <= 1) return;

        var current = 0;
        var timer = null;

        function resetToFirst() {
            if (timer) {
                clearInterval(timer);
                timer = null;
            }
            images[current].classList.remove('img-active');
            current = 0;
            images[0].classList.add('img-active');
        }

        function nextSlide() {
            images[current].classList.remove('img-active');
            current = (current + 1) % images.length;
            images[current].classList.add('img-active');
        }

        function startOnHover() {
            if (timer) clearInterval(timer);
            timer = setInterval(nextSlide, 2500);
        }

        const card = container.closest('.card');
        if (card) {
            card.addEventListener('mouseenter', startOnHover);
            card.addEventListener('mouseleave', resetToFirst);
        }
    });
});
