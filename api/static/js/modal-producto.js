/**
 * ============================================================================
 * modal-producto.js — Modal de producto del catálogo
 * ============================================================================
 *
 * RESPONSABILIDAD:
 *   Controla el modal que se abre al hacer clic en un producto del catálogo.
 *   Muestra información del producto, galería de imágenes, selector de
 *   variantes (color + talla), indicador de stock, y permite agregar al carrito.
 *
 * FLUJO GENERAL (cuando el usuario hace clic en un producto):
 *   1. Se leen los dataset-* del botón (título, categoría, precio, imágenes, variantes)
 *   2. Se renderiza el carrusel de imágenes con las fotos del producto
 *   3. Se extraen los colores únicos de las variantes y se crean los botones de color
 *   4. Al seleccionar un color:
 *      - Se filtran las tallas disponibles para ese color
 *      - Se actualiza el carrusel si la variante tiene imagen propia
 *      - Se actualiza el precio si difiere del precio mínimo
 *   5. Al seleccionar una talla:
 *      - Se muestra el indicador de stock (verde/rojo)
 *      - Se actualiza el precio si difiere del precio mínimo
 *   6. Al hacer clic en "Agregar al carrito":
 *      - Se valida que haya variante seleccionada y stock disponible
 *      - Se llama a agregarAlCarrito() (definida en otro archivo)
 *      - Se muestra toast de confirmación y animación en el badge del carrito
 *
 * DEPENDENCIAS:
 *   - Bootstrap 5 (Carousel, Modal, Toast)
 *   - function agregarAlCarrito() — definida en carrito.js
 *   - window.USER_LOGGED_IN — variable global para controlar visibilidad del formulario de reseña
 *
 * VARIABLES HTML ESPERADAS:
 *   - #modalProducto           — contenedor del modal Bootstrap
 *   - #modalCarouselInner      — slides del carrusel
 *   - #carouselProducto        — elemento raíz del carrusel
 *   - #carouselPrev/Next       — botones de navegación del carrusel
 *   - #carouselIndicadores     — indicadores del carrusel
 *   - #modalTitulo/Categoria/Materiales/Cuidados/Descripcion — info del producto
 *   - #modalPrecio             — precio mostrado
 *   - #colorPicker             — contenedor de botones de color
 *   - #sizePicker              — contenedor de botones de talla
 *   - #carrito-actions         — sección de agregar al carrito
 *   - #varianteSku             — input hidden con el SKU de la variante seleccionada
 *   - #modalStockIcon/Text     — indicador de stock
 *   - #btnAgregarCarrito       — botón de agregar al carrito
 *   - #qtyInput                — input de cantidad
 *   - #cartToast               — toast de confirmación
 *   - #cart-badge              — badge del carrito en el navbar
 *   - #formResena              — formulario de reseñas
 *   - #loginRequerido          — mensaje de login requerido
 *   - .modal-trigger           — botones que abren el modal (en el catálogo)
 *
 * VARIABLES DATA-ATRIBUTOS ESPERADAS EN .modal-trigger:
 *   - data-producto-id         — ID del producto
 *   - data-titulo              — nombre del producto
 *   - data-categoria           — categoría del producto
 *   - data-materiales          — materiales (separados por coma)
 *   - data-cuidados            — instrucciones de cuidado
 *   - data-descripcion         — descripción del producto
 *   - data-precio-min-num      — precio mínimo como número
 *   - data-precio-base         — precio de referencia del producto
 *   - data-imagenes            — JSON array de URLs de imágenes
 *   - data-imagen              — fallback si data-imagenes falla
 *   - data-variantes           — JSON array de objetos variante
 *
 * ESTRUCTURA ESPERADA DE CADA OBJETO VARIANTE:
 *   {
 *     sku: string,              // identificador único (ej: "1-ROJO-M")
 *     precio: number,           // precio de esta variante
 *     stock: number,            // unidades disponibles
 *     imagen: string|null,      // URL de imagen específica de la variante
 *     color: { nombre: string, hex: string } | null,
 *     talla: string             // nombre de la talla (ej: "M", "42")
 *   }
 *
 * BACKUP: api/static/js/modal-producto.js.bak
 */

document.addEventListener('DOMContentLoaded', function () {

    // =========================================================================
    // 1. CLICK EN BOTONES DEL CATÁLOGO — abre el modal de producto
    // =========================================================================
    document.querySelectorAll('.modal-trigger').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();

            // -----------------------------------------------------------------
            // 1.1 Poblar información básica del producto
            // -----------------------------------------------------------------
            const productoId = this.dataset.productoId;
            document.getElementById('modalTitulo').textContent = this.dataset.titulo;
            document.getElementById('modalCategoria').textContent = this.dataset.categoria || 'Sin categoría';
            document.getElementById('modalMateriales').textContent = this.dataset.materiales || 'N/A';
            document.getElementById('modalCuidados').textContent = this.dataset.cuidados || 'N/A';
            document.getElementById('modalDescripcion').textContent = this.dataset.descripcion || '';

            // -----------------------------------------------------------------
            // 1.2 Parsear precios: base (referencia) y mínimo (para catálogo)
            // -----------------------------------------------------------------
            const precioBaseNum = parseFloat(this.dataset.precioBase) || 0;
            const precioMinNum = parseFloat(this.dataset.precioMinNum) || 0;

            // -----------------------------------------------------------------
            // 1.3 Parsear imágenes del producto
            //     Django envía el JSON con comillas simples, por eso se reemplazan
            //     antes de parsear. Si falla, se usa la imagen individual como fallback.
            // -----------------------------------------------------------------
            const imagenesRaw = this.dataset.imagenes || "[]";
            let imagenes = [];
            try {
                imagenes = JSON.parse(imagenesRaw.replace(/'/g, '"'));
            } catch (e) {
                imagenes = [this.dataset.imagen];
            }

            // Referencias a elementos del carrusel (se reutilizan en renderCarousel)
            const carouselInner = document.getElementById('modalCarouselInner');
            const carouselPrev = document.getElementById('carouselPrev');
            const carouselNext = document.getElementById('carouselNext');
            const carouselIndicadores = document.getElementById('carouselIndicadores');

            // -----------------------------------------------------------------
            // renderCarousel(imgs) — Reconstruye el carrusel con un array de URLs
            // -----------------------------------------------------------------
            // Se llama al abrir el modal y cada vez que cambia el color seleccionado,
            // para mostrar la imagen de la variante de ese color primero.
            function renderCarousel(imgs) {
                carouselInner.innerHTML = '';
                carouselIndicadores.innerHTML = '';

                const imgsFinal = imgs.length > 0 ? imgs : ['https://placehold.co/400x280?text=Sin+Imagen'];

                imgsFinal.forEach((url, index) => {
                    carouselInner.innerHTML += `
                        <div class="carousel-item ${index === 0 ? 'active' : ''}" style="height:100%;">
                            <img src="${url}" class="d-block w-100 h-100" style="object-fit:cover;" alt="Imagen ${index + 1}">
                        </div>
                    `;
                    carouselIndicadores.innerHTML += `
                        <button type="button" data-bs-target="#carouselProducto" data-bs-slide-to="${index}"
                                class="${index === 0 ? 'active' : ''}" aria-current="${index === 0 ? 'true' : 'false'}">
                        </button>
                    `;
                });

                // Solo se muestran flechas e indicadores si hay más de 1 imagen
                carouselPrev.style.display = imgsFinal.length > 1 ? 'block' : 'none';
                carouselNext.style.display = imgsFinal.length > 1 ? 'block' : 'none';
                carouselIndicadores.style.display = imgsFinal.length > 1 ? 'flex' : 'none';

                // Se resetea el carrusel a la primera imagen (necesario si el usuario
                // navegó antes de cambiar de color, y el carrusel ya estaba en otra posición)
                const carouselEl = document.getElementById('carouselProducto');
                const carouselInstance = bootstrap.Carousel.getOrCreateInstance(carouselEl);
                carouselInstance.to(0);
            }

            renderCarousel(imagenes);

            // -----------------------------------------------------------------
            // 1.4 Parsear variantes (colores + tallas + stock + precios)
            // -----------------------------------------------------------------
            let variantes = [];
            try {
                const raw = this.dataset.variantes || '[]';
                variantes = JSON.parse(raw.replace(/'/g, '"'));
            } catch (e) {
                console.error('Error parseando variantes:', e, this.dataset.variantes);
            }

            // Referencias a elementos del selector de variantes
            const coloresContainer = document.getElementById('colorPicker');
            const sizePicker = document.getElementById('sizePicker');
            const carritoActions = document.getElementById('carrito-actions');
            const varianteSkuInput = document.getElementById('varianteSku');
            const stockIcon = document.getElementById('modalStockIcon');
            const stockText = document.getElementById('modalStockText');

            // Estado del modal: qué variante y color están seleccionados
            let varianteSeleccionada = null;
            let colorSeleccionado = null;

            // -----------------------------------------------------------------
            // actualizarStockDisplay(variante) — Actualiza el indicador visual
            // -----------------------------------------------------------------
            // Muestra un círculo verde + texto si hay stock, rojo si no.
            // Se llama cuando se selecciona una talla o cuando no hay selección.
            function actualizarStockDisplay(variante) {
                if (!variante) {
                    stockIcon.style.backgroundColor = '#ef4444';
                    stockText.textContent = 'Selecciona una variante para visualizar el producto';
                    stockText.className = 'text-muted fw-medium small';
                    return;
                }
                if (variante.stock > 0) {
                    stockIcon.style.backgroundColor = '#10b981';
                    stockText.textContent = `Disponible (${variante.stock} unidades)`;
                    stockText.className = 'text-success fw-medium small';
                } else {
                    stockIcon.style.backgroundColor = '#ef4444';
                    stockText.textContent = 'Agotado';
                    stockText.className = 'text-danger fw-medium small';
                }
            }

            // -----------------------------------------------------------------
            // llenarSizePicker(color) — Construye los botones de talla
            // -----------------------------------------------------------------
            // Filtra las variantes por el color seleccionado y crea un botón
            // tipo radio por cada talla disponible. Incluye el stock entre
            // paréntesis para que el usuario vea disponibilidad.
            //
            // Auto-selección: al renderizar, selecciona automáticamente la
            // primera variante con stock para agilizar la experiencia.
            //
            // Se llama:
            //   - Al abrir el modal (con el primer color)
            //   - Cada vez que cambia la selección de color
            function llenarSizePicker(color) {
                sizePicker.innerHTML = '';

                const variantesFiltradas = color
                    ? variantes.filter(v => v.color && v.color.nombre === color)
                    : variantes;

                if (variantesFiltradas.length === 0) return;

                let primerConStock = null;

                variantesFiltradas.forEach(v => {
                    const id = `size-${v.sku}`;
                    const disabled = v.stock <= 0;

                    const label = document.createElement('label');
                    label.className = `btn btn-sm rounded-pill px-3 size-option ${disabled ? 'disabled opacity-50' : 'btn-outline-brand'}`;
                    label.setAttribute('for', id);
                    label.innerHTML = `${v.talla} <small class="ms-1 opacity-75">(${v.stock})</small>`;

                    const input = document.createElement('input');
                    input.type = 'radio';
                    input.className = 'btn-check size-radio';
                    input.name = 'tallaSeleccionada';
                    input.id = id;
                    input.value = v.sku;
                    input.autocomplete = 'off';

                    // Se guarda la primera variante con stock para auto-seleccionar
                    if (!disabled && !primerConStock) {
                        primerConStock = v;
                    }

                    // Click en una talla: actualiza estado visual, stock y precio
                    label.addEventListener('click', function () {
                        if (disabled) {
                            actualizarStockDisplay({ stock: 0 });
                            document.getElementById('btnAgregarCarrito').disabled = true;
                            return;
                        }

                        // Resetear estilo de todas las tallas y resaltar la seleccionada
                        document.querySelectorAll('.size-option').forEach(el => {
                            el.className = `btn btn-sm rounded-pill px-3 size-option btn-outline-brand`;
                        });
                        this.className = `btn btn-sm rounded-pill px-3 size-option btn-brand`;

                        varianteSeleccionada = v;
                        varianteSkuInput.value = v.sku;

                        actualizarStockDisplay(v);

                        // Habilitar el botón porque hay una variante válida seleccionada
                        document.getElementById('btnAgregarCarrito').disabled = false;

                        // Si la variante es más barata que el precio base, mostrar descuento.
                        // Si es igual o más cara, mostrar solo el precio de la variante.
                        if (v.precio && v.precio < precioBaseNum) {
                            const el = document.getElementById('modalPrecio');
                            el.innerHTML = `$ ${v.precio.toFixed(0)} MXN <small class="text-muted fw-normal fs-6"><s>$${precioBaseNum.toFixed(0)} MXN</s></small>`;
                        } else if (v.precio) {
                            document.getElementById('modalPrecio').innerHTML = `$ ${v.precio.toFixed(0)} MXN`;
                        } else {
                            document.getElementById('modalPrecio').innerHTML = `$ ${precioBaseNum.toFixed(0)} MXN`;
                        }
                    });

                    sizePicker.appendChild(input);
                    sizePicker.appendChild(label);
                });

                // Auto-seleccionar la primera variante con stock
                if (primerConStock) {
                    const firstInput = document.getElementById(`size-${primerConStock.sku}`);
                    if (firstInput) {
                        firstInput.checked = true;
                        const firstLabel = document.querySelector(`label[for="size-${primerConStock.sku}"]`);
                        if (firstLabel) {
                            firstLabel.className = `btn btn-sm rounded-pill px-3 size-option btn-brand`;
                        }
                    }
                    varianteSeleccionada = primerConStock;
                    varianteSkuInput.value = primerConStock.sku;
                    actualizarStockDisplay(primerConStock);

                    // Mostrar precio correcto de la variante auto-seleccionada
                    if (primerConStock.precio && primerConStock.precio < precioBaseNum) {
                        document.getElementById('modalPrecio').innerHTML =
                            `$ ${primerConStock.precio.toFixed(0)} MXN <small class="text-muted fw-normal fs-6"><s>$${precioBaseNum.toFixed(0)} MXN</s></small>`;
                    } else if (primerConStock.precio) {
                        document.getElementById('modalPrecio').innerHTML =
                            `$ ${primerConStock.precio.toFixed(0)} MXN`;
                    }

                    // Habilitar botón porque hay una variante con stock auto-seleccionada
                    const btnAuto = document.getElementById('btnAgregarCarrito');
                    if (btnAuto) btnAuto.disabled = false;
                } else {
                    varianteSeleccionada = null;
                    varianteSkuInput.value = '';
                    actualizarStockDisplay(null);
                    document.getElementById('modalPrecio').innerHTML = `$ ${precioBaseNum.toFixed(0)} MXN`;

                    // Deshabilitar botón porque no hay variante con stock
                    const btnAuto = document.getElementById('btnAgregarCarrito');
                    if (btnAuto) btnAuto.disabled = true;
                }
            }

            // -----------------------------------------------------------------
            // llenarColorPicker() — Construye los botones de color
            // -----------------------------------------------------------------
            // Extrae los colores únicos de todas las variantes, crea un botón
            // tipo radio por cada uno con un círculo del color + nombre.
            //
            // Al hacer clic en un color:
            //   1. Se re-renderiza el carrusel con la imagen de esa variante primero
            //   2. Se actualiza el precio si difiere del mínimo
            //   3. Se reconstruyen los botones de talla para ese color
            //
            // Se llama una vez al abrir el modal, y el primer color queda
            // pre-seleccionado.
            function llenarColorPicker() {
                coloresContainer.innerHTML = '';

                // Extraer colores únicos usando Set para evitar duplicados
                const coloresUnicos = [];
                const vistos = new Set();

                variantes.forEach(v => {
                    if (v.color && !vistos.has(v.color.nombre)) {
                        vistos.add(v.color.nombre);
                        coloresUnicos.push(v.color);
                    }
                });

                if (coloresUnicos.length === 0) {
                    coloresContainer.innerHTML = '<span class="text-muted small">N/A</span>';
                    llenarSizePicker(null);
                    return;
                }

                coloresUnicos.forEach((color, index) => {
                    // Se usa el nombre del color como ID (reemplazando espacios por guiones)
                    const id = `color-${color.nombre.replace(/\s+/g, '-')}`;

                    const label = document.createElement('label');
                    label.className = `btn btn-sm rounded-pill px-3 d-inline-flex align-items-center gap-2 color-option ${index === 0 ? 'btn-brand' : 'btn-outline-brand'}`;
                    label.setAttribute('for', id);
                    label.innerHTML = `
                        <span style="display:inline-block;width:14px;height:14px;background:${color.hex};border-radius:50%;border:1px solid #ccc;"></span>
                        ${color.nombre}
                    `;

                    const input = document.createElement('input');
                    input.type = 'radio';
                    input.className = 'btn-check color-radio';
                    input.name = 'colorSeleccionado';
                    input.id = id;
                    input.value = color.nombre;
                    input.autocomplete = 'off';

                    if (index === 0) input.checked = true;

                    // Click en un color: actualizar carrusel, precio y tallas
                    label.addEventListener('click', function () {
                        if (colorSeleccionado === color.nombre) return;
                        colorSeleccionado = color.nombre;

                        // Resetear estilo de todos los colores y resaltar el seleccionado
                        document.querySelectorAll('.color-option').forEach(el => {
                            el.className = `btn btn-sm rounded-pill px-3 d-inline-flex align-items-center gap-2 color-option btn-outline-brand`;
                        });
                        this.className = `btn btn-sm rounded-pill px-3 d-inline-flex align-items-center gap-2 color-option btn-brand`;

                        // Si la variante de este color tiene imagen propia, se muestra
                        // solo esa imagen en el carrusel (sin las imágenes generales)
                        const varianteConImagen = variantes.find(v =>
                            v.color && v.color.nombre === color.nombre && v.imagen
                        );
                        if (varianteConImagen) {
                            renderCarousel([varianteConImagen.imagen]);
                        } else {
                            renderCarousel(imagenes);
                        }

                        // Si la primera variante de este color es más barata que el precio base,
                        // mostrar descuento. Si no, mostrar su precio normal.
                        const varianteDelColor = variantes.find(v =>
                            v.color && v.color.nombre === color.nombre && v.precio
                        );
                        if (varianteDelColor && varianteDelColor.precio < precioBaseNum) {
                            const el = document.getElementById('modalPrecio');
                            el.innerHTML = `$ ${varianteDelColor.precio.toFixed(0)} MXN <small class="text-muted fw-normal fs-6"><s>$${precioBaseNum.toFixed(0)} MXN</s></small>`;
                        } else if (varianteDelColor) {
                            document.getElementById('modalPrecio').innerHTML = `$ ${varianteDelColor.precio.toFixed(0)} MXN`;
                        } else {
                            document.getElementById('modalPrecio').innerHTML = `$ ${precioBaseNum.toFixed(0)} MXN`;
                        }

                        // Reconstruir las tallas disponibles para este color
                        llenarSizePicker(color.nombre);
                    });

                    coloresContainer.appendChild(input);
                    coloresContainer.appendChild(label);
                });

                // Auto-seleccionar el primer color y renderizar sus tallas + imagen
                if (coloresUnicos.length > 0) {
                    colorSeleccionado = coloresUnicos[0].nombre;
                    llenarSizePicker(colorSeleccionado);

                    const primerConImagen = variantes.find(v =>
                        v.color && v.color.nombre === colorSeleccionado && v.imagen
                    );
                    if (primerConImagen) {
                        renderCarousel([primerConImagen.imagen]);
                    }
                }
            }

            llenarColorPicker();

            // -----------------------------------------------------------------
            // 1.5 Mostrar/ocultar sección de carrito según stock total
            // -----------------------------------------------------------------
            // Si ninguna variante tiene stock, se oculta el botón de agregar
            const count = variantes.reduce((sum, v) => sum + v.stock, 0);
            carritoActions.style.display = count > 0 ? 'block' : 'none';

            // -----------------------------------------------------------------
            // 1.6 Configurar botón "Agregar al carrito"
            // -----------------------------------------------------------------
            // Se clona el botón para eliminar event listeners previos (si el usuario
            // abre el mismo modal dos veces, se acumularían listeners y se ejecutaría
            // el click dos veces). Se reemplaza el original con la copia limpia.
            const btnAgregar = document.getElementById('btnAgregarCarrito');
            if (btnAgregar) {
                const nuevoBtn = btnAgregar.cloneNode(true);
                btnAgregar.parentNode.replaceChild(nuevoBtn, btnAgregar);

                nuevoBtn.addEventListener('click', function () {
                    const sku = varianteSkuInput.value;
                    if (!sku) {
                        alert('Selecciona un color y una talla primero.');
                        return;
                    }

                    const variante = variantes.find(v => v.sku === sku);
                    if (!variante) {
                        alert('Variante no encontrada.');
                        return;
                    }

                    const cantidad = parseInt(document.getElementById('qtyInput').value) || 1;
                    if (cantidad > variante.stock) {
                        alert(`Solo hay ${variante.stock} unidades disponibles para esta variante.`);
                        return;
                    }

                    // Se usa el precio de la variante si existe, si no el precio mínimo
                    const precioFinal = variante.precio || precioMinNum;
                    const imagenFinal = variante.imagen || (imagenes.length > 0 ? imagenes[0] : '');
                    const colorNombre = variante.color ? variante.color.nombre : '';
                    const tallaNombre = variante.talla || '';

                    agregarAlCarrito(productoId, this.dataset.productoNombre || document.getElementById('modalTitulo').textContent, precioFinal, imagenFinal, tallaNombre, cantidad, sku, colorNombre);

                    // Toast de confirmación
                    const toastEl = document.getElementById('cartToast');
                    if (toastEl) {
                        document.getElementById('toastProductName').textContent =
                            this.dataset.productoNombre || document.getElementById('modalTitulo').textContent;
                        const detalle = `${colorNombre ? colorNombre + ' \u00B7 ' : ''}Talla ${tallaNombre} \u00B7 ${cantidad} ${cantidad === 1 ? 'unidad' : 'unidades'}`;
                        document.getElementById('toastProductDetail').textContent = detalle;
                        const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
                        toast.show();
                    }

                    // Animación de rebote en el badge del carrito
                    // void badge.offsetWidth fuerza un reflow para reiniciar la animación CSS
                    const badge = document.getElementById('cart-badge');
                    if (badge) {
                        badge.classList.remove('cart-bounce');
                        void badge.offsetWidth;
                        badge.classList.add('cart-bounce');
                        setTimeout(() => badge.classList.remove('cart-bounce'), 600);
                    }

                    // Feedback visual: el botón muestra "Agregado ✓" por 1.5 segundos
                    const originalText = nuevoBtn.innerHTML;
                    nuevoBtn.innerHTML = '<span class="material-symbols-outlined me-2 fs-5">check</span> Agregado \u2713';
                    nuevoBtn.disabled = true;
                    setTimeout(() => {
                        nuevoBtn.innerHTML = originalText;
                        nuevoBtn.disabled = false;
                    }, 1500);
                });

                nuevoBtn.dataset.productoNombre = this.dataset.titulo;

                // Inicialmente deshabilitado hasta que se seleccione una variante con stock
                nuevoBtn.disabled = true;
            }

            // -----------------------------------------------------------------
            // 1.7 Configurar formulario de reseñas
            // -----------------------------------------------------------------
            document.getElementById('modalProductoId').value = productoId;
            document.getElementById('formResena').action = `/talcahualme/producto/${productoId}/resena/`;

            const formResena = document.getElementById('formResena');
            const loginRequerido = document.getElementById('loginRequerido');

            // Se muestra el formulario solo si el usuario está logueado,
            // si no se muestra el mensaje de "inicia sesión"
            if (window.USER_LOGGED_IN === true || window.USER_LOGGED_IN === 'true') {
                formResena.style.display = 'block';
                loginRequerido.style.display = 'none';
            } else {
                formResena.style.display = 'none';
                loginRequerido.style.display = 'block';
            }

            formResena.action = `/talcahualme/producto/${productoId}/resena/`;
            new bootstrap.Modal(document.getElementById('modalProducto')).show();
        });
    });

    // =========================================================================
    // 2. ENVÍO DEL FORMULARIO DE RESEÑA — feedback de carga
    // =========================================================================
    // Se deshabilita el botón y se muestra un spinner para evitar envíos dobles
    const formResena = document.getElementById('formResena');
    if (formResena) {
        formResena.addEventListener('submit', function () {
            const btn = document.getElementById('btnResena');
            btn.disabled = true;
            btn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Publicando...
            `;
        });
    }

    // =========================================================================
    // 3. CONTROLES DE CANTIDAD (+/-) — validación de rango 1-99
    // =========================================================================
    const qtyInput = document.getElementById('qtyInput');
    const btnMinus = document.getElementById('btnQtyMinus');
    const btnPlus = document.getElementById('btnQtyPlus');

    if (qtyInput && btnMinus && btnPlus) {
        btnMinus.addEventListener('click', function () {
            let val = parseInt(qtyInput.value) || 1;
            if (val > 1) qtyInput.value = val - 1;
        });
        btnPlus.addEventListener('click', function () {
            let val = parseInt(qtyInput.value) || 1;
            if (val < 99) qtyInput.value = val + 1;
        });
        qtyInput.addEventListener('change', function () {
            let val = parseInt(this.value) || 1;
            if (val < 1) val = 1;
            if (val > 99) val = 99;
            this.value = val;
        });
    }
});
