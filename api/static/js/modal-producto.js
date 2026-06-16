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

            // --- SIZE PICKER: poblar tallas seleccionables ---
            const sizePicker = document.getElementById('sizePicker'); // Optengo el contenedor donde van las tallas para agregarle los botones de talla dinamicamente
            const carritoActions = document.getElementById('carrito-actions'); // Contenedor del botón de agregar al carrito, lo mostramos o ocultamos dependiendo si hay tallas disponibles, si no hay tallas no tiene sentido mostrar el botón de agregar al carrito porque no se podría seleccionar una talla
            if (!sizePicker) return; // Si no encontramos el contenedor de tallas, no hacemos nada

            sizePicker.innerHTML = ''; // Limpiamos las tallas anteriores, Sin esto, cada vez que abres un producto nuevo se acumularían las tallas del anterior.

            if (stockTallas.some(t => t.stock > 0)) { // Si hay tallas con stock
                carritoActions.style.display = 'block'; // Mostramos toda la seccion de acciones de carrito (que incluye el botón de agregar al carrito y el selector de cantidad) si hay tallas disponibles

                // Recorremos el array de tallas con stock, por cada talla creamos un botón tipo radio para que el usuario pueda seleccionar una talla, también agregamos un event listener para cambiar el estilo del botón seleccionado cuando se clickea
                stockTallas.forEach((item, index) => {
                    const id = `size-${item.talla}`; // Creamos un id único para el input y su label asociado, esto es necesario para que al hacer click en el label se seleccione el input radio correspondiente, usamos la talla como parte del id para asegurarnos que sea único por producto
                    const disabled = item.stock <= 0 ? 'disabled' : ''; // Si el stock de esa talla es 0 o menos, el botón se muestra deshabilitado y con opacidad reducida
                    const label = document.createElement('label'); // Creamos el label que actúa como botón visible para el usuario, el input radio estará oculto pero el label es lo que el usuario verá y clickeá para seleccionar la talla
                    label.className = `btn btn-sm rounded-pill px-3 size-option ${disabled ? 'disabled opacity-50' : ''} ${index === 0 ? 'btn-primary text-white' : 'btn-outline-secondary'}`;
                    label.setAttribute('for', id); // Asociamos el id del input radio con el label, esto hace que al hacer click en el label se seleccione el input radio correspondiente
                    label.innerHTML = `${item.talla} <small class="ms-1 opacity-75">(${item.stock})</small>`;

                    // Input radio oculto para seleccionar la talla, el name es el mismo para todos los radios para que solo se pueda seleccionar uno, el id es único para cada talla y se asocia con el label, el value es la talla que se seleccionará cuando se elija ese radio
                    const input = document.createElement('input');
                    input.type = 'radio';
                    input.className = 'btn-check size-radio';
                    input.name = 'tallaSeleccionada';
                    input.id = id;
                    input.value = item.talla;
                    input.autocomplete = 'off';
                    if (index === 0 && !disabled) input.checked = true; // Si es la primera talla y no esta deshabilitada, la seleccionamos por defecto

                    // Click en label: actualizar estilo
                    label.addEventListener('click', function() {
                        if (disabled) return;
                        document.querySelectorAll('.size-option').forEach(el => {
                            el.className = `btn btn-sm rounded-pill px-3 size-option btn-outline-secondary`;
                        });
                        this.className = `btn btn-sm rounded-pill px-3 size-option btn-primary text-white`;
                    });

                    // Agregamos el input radio y el label al contenedor de tallas
                    sizePicker.appendChild(input); // con el appendChild agregamos el input radio al contenedor
                    sizePicker.appendChild(label);
                });
            } else {
                carritoActions.style.display = 'none'; // Ocultamos el botón de agregar al carrito si no hay tallas disponibles
            }

            // --- Botón "Agregar al canasto" ---
            const btnAgregar = document.getElementById('btnAgregarCarrito');
            if (btnAgregar) {
                /*
                Quitar event listeners anteriores clonando, 
                esto para evitar que se dupliquen los event listeners cada vez que se abre el modal con un producto diferente, 
                sin esto, si abres un producto, luego otro, y haces click en agregar al carrito, 
                se ejecutarían los event listeners de ambos productos acumulados, 
                lo que causaría que se agregue el último producto varias veces al carrito dependiendo de cuántos productos hayas abierto.
                */
                const nuevoBtn = btnAgregar.cloneNode(true);
                btnAgregar.parentNode.replaceChild(nuevoBtn, btnAgregar); // Reemplazamos el botón antiguo con el nuevo

                // Event listener para agregar al carrito
                nuevoBtn.addEventListener('click', function() {
                    const selectedRadio = document.querySelector('.size-radio:checked'); // Obtenemos el input radio seleccionado
                    if (!selectedRadio) {
                        alert('Selecciona una talla primero.');
                        return;
                    }
                    const talla = selectedRadio.value;
                    const cantidad = parseInt(document.getElementById('qtyInput').value) || 1;
                    const productoId = document.getElementById('modalProductoId').value;

                    const tallaData = stockTallas.find(t => t.talla === talla); // Buscamos el stock de la talla seleccionada
                    if (tallaData && cantidad > tallaData.stock) {
                        alert(`Solo hay ${tallaData.stock} unidades disponibles en talla ${talla}.`);
                        return;
                    }

                    const imagen = imagenes.length > 0 ? imagenes[0] : ''; // Si no hay imagenes, usamos la imagen principal

                    // Usamos la función agregarAlCarrito para agregar el producto al carrito
                    // Con dataset es para acceder a los datos del producto desde el modal de producto, si no encuentra el dato en el dataset, usa un valor por defecto (como el título del modal o 0 para el precio)
                    agregarAlCarrito(productoId, this.dataset.productoNombre || document.getElementById('modalTitulo').textContent, this.dataset.productoPrecio || '0', imagen, talla, cantidad);

                    // Feedback visual para el usuario, cambiamos el texto del botón temporalmente para indicar que se agregó al carrito, y luego lo volvemos a su estado original después de 1.5 segundos
                    const originalText = nuevoBtn.innerHTML;
                    nuevoBtn.innerHTML = '<span class="material-symbols-outlined me-2 fs-5">check</span> Agregado ✓';
                    nuevoBtn.disabled = true;
                    setTimeout(() => {
                        nuevoBtn.innerHTML = originalText;
                        nuevoBtn.disabled = false;
                    }, 1500);
                });
                // Guardar datos del producto en el botón
                nuevoBtn.dataset.productoNombre = this.dataset.titulo;
                nuevoBtn.dataset.productoPrecio = this.dataset.precio ? this.dataset.precio.replace(/[^0-9.]/g, '') : '0';
            }

            // --- Reseña ---
            const productoId = this.dataset.productoId;
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

    // Loading state en formulario de reseña
    const formResena = document.getElementById('formResena');
    if (formResena) {
        formResena.addEventListener('submit', function() {
            const btn = document.getElementById('btnResena');
            btn.disabled = true;
            btn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Publicando...
            `;
        });
    }

    // --- Controles de cantidad (+/-) ---
    const qtyInput = document.getElementById('qtyInput');
    const btnMinus = document.getElementById('btnQtyMinus');
    const btnPlus = document.getElementById('btnQtyPlus');

    if (qtyInput && btnMinus && btnPlus) {
        btnMinus.addEventListener('click', function() {
            let val = parseInt(qtyInput.value) || 1;
            if (val > 1) qtyInput.value = val - 1;
        });
        btnPlus.addEventListener('click', function() {
            let val = parseInt(qtyInput.value) || 1;
            if (val < 99) qtyInput.value = val + 1;
        });
        qtyInput.addEventListener('change', function() {
            let val = parseInt(this.value) || 1;
            if (val < 1) val = 1;
            if (val > 99) val = 99;
            this.value = val;
        });
    }
});
