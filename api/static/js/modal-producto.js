document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal-trigger').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();

            // Datos básicos
            document.getElementById('modalTitulo').textContent = this.dataset.titulo;
            document.getElementById('modalPrecio').textContent = this.dataset.precio;
            document.getElementById('modalCategoria').textContent = this.dataset.categoria || 'Sin categoría';
            
            // NUEVOS DATOS
            //document.getElementById('modalTallas').textContent = this.dataset.tallas || 'N/A';
            document.getElementById('modalMateriales').textContent = this.dataset.materiales || 'N/A';
            document.getElementById('modalCuidados').textContent = this.dataset.cuidados || 'N/A';
            document.getElementById('modalDescripcion').textContent = this.dataset.descripcion || '';

            // Construir carousel de imágenes
            const imagenesRaw = this.dataset.imagenes || "[]"; // Obtener las imagenes de dataset y las parsear
            let imagenes = []; // Array para almacenar las imagenes

            // Usamos try catch para parsear el JSON
            try {
                imagenes = JSON.parse(imagenesRaw.replace(/'/g, '"')); // Reemplazar las comillas simples por comillas dobles
            } catch(e) {
                imagenes = [this.dataset.imagen]; // Si falla, usamos la imagen principal
            }

            // Elementos del DOM
            const carouselInner = document.getElementById('modalCarouselInner');
            const carouselPrev = document.getElementById('carouselPrev');
            const carouselNext = document.getElementById('carouselNext');
            const carouselIndicadores = document.getElementById('carouselIndicadores');

            // Limpiar carousel anterior, Sin esto, cada vez que abres un producto nuevo se acumularían las imágenes del anterior.
            carouselInner.innerHTML = '';
            carouselIndicadores.innerHTML = ''; // Limpiar indicadores / las barras

            if (imagenes.length === 0) { // Si no hay imagenes
                imagenes = ['https://placehold.co/400x280?text=Sin+Imagen'];
            }

            // Construir slides
            // Recorremos el array de imagenes, index es posicion (0, 1, 2...), el primero es la imagen principal
            // La primera imagen se agrega la clase active porque Bootstrap necesita que exactamente un slide esté activo al inicio
            imagenes.forEach((url, index) => {
                carouselInner.innerHTML += `
                    <div class="carousel-item ${index === 0 ? 'active' : ''}" style="height:100%;">
                        <img src="${url}" class="d-block w-100 h-100" style="object-fit:cover;" alt="Imagen ${index + 1}">
                    </div>
                `;
                // Indicadores
                // Por cada imagen también crea un punto indicador abajo del carousel. data-bs-slide-to le dice a Bootstrap a qué slide ir cuando se clickea ese punto
                carouselIndicadores.innerHTML += `
                    <button type="button" data-bs-target="#carouselProducto" data-bs-slide-to="${index}" 
                            class="${index === 0 ? 'active' : ''}" aria-current="${index === 0 ? 'true' : 'false'}">
                    </button>
                `;
            });

            // Mostrar controles solo si hay más de 1 imagen
            if (imagenes.length > 1) {
                carouselPrev.style.display = 'block';
                carouselNext.style.display = 'block';
                carouselIndicadores.style.display = 'flex';
            } else {
                carouselPrev.style.display = 'none';
                carouselNext.style.display = 'none';
                carouselIndicadores.style.display = 'none';
            }

            // Reiniciar el carousel de Bootstrap
            const carouselEl = document.getElementById('carouselProducto');
            const carouselInstance = bootstrap.Carousel.getOrCreateInstance(carouselEl);
            carouselInstance.to(0);

            // Tallas
            let stockTallas = [];
            try {
                const raw = this.dataset.stockTallas || '[]';
                stockTallas = JSON.parse(raw.replace(/'/g, '"'));
            } catch(e) {
                console.error('Error parseando stock tallas:', e, this.dataset.stockTallas);
            }

            const modalTallas = document.getElementById('modalTallas');
            if (stockTallas.length > 0) {
                modalTallas.innerHTML = stockTallas.map(item => {
                    return `<span class="badge bg-info text-dark me-1">
                                ${item.talla} 
                                <span class="badge bg-dark ms-1">${item.stock}</span>
                            </span>`;
                }).join('');
            } else {
                modalTallas.textContent = 'N/A';
            }

            // Stock
            const stock = parseInt(this.dataset.stock) || 0;
            const stockIcon = document.getElementById('modalStockIcon');
            const stockText = document.getElementById('modalStockText');
            if (stock > 0) {
                stockIcon.style.backgroundColor = '#10b981';
                stockText.textContent = `Disponible (${stock} unidades)`;
                stockText.className = 'text-success fw-medium small';
            } else {
                stockIcon.style.backgroundColor = '#ef4444';
                stockText.textContent = 'Agotado';
                stockText.className = 'text-danger fw-medium small';
            }

            const productoId = this.dataset.productoId; //Obtenemos el id del producto para que se pueda cargar el modal con su producto
            console.log('productoId:', productoId);
            console.log('dataset:', this.dataset);
            // Aqui obteneremos el id del producto que se clickeo
            document.getElementById('modalProductoId').value = productoId;
            // Aqui hacemos la accion del formulario de resena con el id del producto para guardar la resena
            document.getElementById('formResena').action = `/talcahualme/producto/${productoId}/resena/`;

            // Creamos variables constantes para pasarle los modales de resena y login
            const formResena = document.getElementById('formResena');
            const loginRequerido = document.getElementById('loginRequerido');

            // Mostrar el formulario de resena si el usuario esta logueado
            if (window.USER_LOGGED_IN === true || window.USER_LOGGED_IN === 'true') {
                console.log('MOSTRANDO formulario - Usuario logueado');
                formResena.style.display = 'block'; // Mostramos el formulario
                loginRequerido.style.display = 'none'; // No mostramos el mensaje
            } else {
                console.log('MOSTRANDO mensaje login - Usuario NO logueado');
                formResena.style.display = 'none'; // No mostramos el formulario
                loginRequerido.style.display = 'block'; // Mostramos el mensaje que necesita loguearse
            }

            console.log('ANTES modal - action:', formResena.action);
            formResena.action = `/talcahualme/producto/${productoId}/resena/`;
            console.log('DESPUÉS set - action:', formResena.action);
            console.log('FINAL - action:', formResena.action);

            new bootstrap.Modal(document.getElementById('modalProducto')).show();
        });
    });

    // ✅ UX MÍNIMA: Solo loading state
    const formResena = document.getElementById('formResena');
    if (formResena) {
       // console.log('productoId:', document.querySelector('.modal-trigger').dataset.productoId);
//console.log('Form action:', document.getElementById('formResena').action);

        formResena.addEventListener('submit', function(e) {
            const btn = document.getElementById('btnResena');
            btn.disabled = true;
            btn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Publicando...
            `;
            // ✅ DJANGO PROCESA - sin e.preventDefault()
        });
    }
});


