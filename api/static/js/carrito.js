// carrito.js — Funcionalidad del carrito de compras

/*
Creamos una variable global para el carrito, que se inicializa con los datos del localStorage o como un array vacío
Cada item del carrito tendrá una estructura como:
{
     key: 'productoId-talla', // clave única para identificar el producto + talla (legacy)
     id: productoId,          // ID del producto
     nombre: 'Nombre del producto',
     precio: 100.00,         // Precio unitario
     imagen: 'url_imagen',   // URL de la imagen del producto
     talla: 'M',             // Talla seleccionada
     cantidad: 2,            // Cantidad seleccionada
     sku: 'PROD-ROJO-M',    // (nuevo) SKU de la variante seleccionada
     color: 'Rojo'           // (nuevo) Nombre del color seleccionado
}
*/
let carrito;
try {
    carrito = JSON.parse(localStorage.getItem('carrito')) || [];
} catch (err) {
    console.error('carrito.js: error parseando localStorage.carrito:', err);
    carrito = [];
    try {
        localStorage.setItem('carrito', JSON.stringify(carrito));
    } catch (e) {
        console.error('carrito.js: no se pudo resetear localStorage.carrito', e);
    }
}

console.log('carrito.js cargado — carrito inicial:', carrito);


// Función para obtener la clave única del producto + variante, esto nos ayuda a manejar productos con diferentes variantes como items separados en el carrito
// Si hay SKU lo usa como key; si no (legacy), usa productoId-talla
function obtenerKey(productoId, talla, sku) {
    if (sku) return `${productoId}-${sku}`;
    return `${productoId}-${talla}`;
}

// Función para agregar un producto al carrito, si el producto con la misma variante ya existe, simplemente aumentamos la cantidad, si no, lo agregamos como un nuevo item
// soporta sku (variante) y colorName para el nuevo sistema de variantes
function agregarAlCarrito(productoId, nombre, precio, imagen, talla, cantidad, sku, colorName) {
    const key = obtenerKey(productoId, talla, sku);
    const existe = carrito.find(item => item.key === key);

    console.log('agregarAlCarrito llamado', { productoId, talla, cantidad, key, precio, nombre, sku, color: colorName });

    if (existe) {
        existe.cantidad += cantidad;
    } else {
        // Si el producto no existe en el carrito, lo agregamos como un nuevo item
        carrito.push({ key, id: productoId, nombre, precio: parseFloat(precio), imagen, talla, cantidad });
    }

    // Guardamos el carrito actualizado en el localStorage y actualizamos la interfaz del carrito
    try {
        localStorage.setItem('carrito', JSON.stringify(carrito));
        console.log('carrito guardado en localStorage', carrito);
    } catch (e) {
        console.error('carrito.js: error guardando carrito en localStorage', e, carrito);
    }
    actualizarBadgeCarrito();
    renderizarOffcanvas(); // Re-renderizamos el offcanvas para mostrar los cambios inmediatamente
}

// Función para eliminar un producto del carrito, filtramos el carrito para eliminar el item con la clave especificada
function eliminarDelCarrito(key) {
    // Filtro en donde solo quiero los items que sean diferentes al que quiero eliminar
    console.log('eliminarDelCarrito llamado', key);
    carrito = carrito.filter(item => item.key !== key);
    try {
        localStorage.setItem('carrito', JSON.stringify(carrito)); // Guardamos el carrito actualizado en el localStorage
        console.log('carrito guardado en localStorage tras eliminar', carrito);
    } catch (e) {
        console.error('carrito.js: error guardando carrito tras eliminar', e, carrito);
    }
    actualizarBadgeCarrito();
    renderizarOffcanvas();
}

function cambiarCantidad(key, cantidad) {
    const item = carrito.find(item => item.key === key); // Buscamos el item en el carrito
    if (!item) return; // Si no encontramos el item, no hacemos nada
    const nueva = item.cantidad + cantidad; // Calculamos la nueva cantidad sumando la cantidad actual con la cantidad que queremos cambiar (puede ser positiva o negativa)
    if (nueva < 1) {
        eliminarDelCarrito(key);
        return;
    }
    item.cantidad = nueva; // Actualizamos la cantidad del item para reflejar los cambios en el carrito
    try {
        localStorage.setItem('carrito', JSON.stringify(carrito)); // Guardamos el carrito actualizado en el localStorage
        console.log('carrito guardado en localStorage tras cambio cantidad', carrito);
    } catch (e) {
        console.error('carrito.js: error guardando carrito tras cambiar cantidad', e, carrito);
    }
    actualizarBadgeCarrito();
    renderizarOffcanvas();
}

// Función para calcular el total del carrito, sumamos el precio de cada item multiplicado por su cantidad
function calcularTotal() {
    /*
    reduce es un metodo que nos permite recorrer un array y aplicar una operacion a cada elemento del array,
    total es el acumulador y item es el elemento actual 
    */
    return carrito.reduce((total, item) => total + (item.precio * item.cantidad), 0);
}

// Función para calcular la cantidad total de items en el carrito, sumamos la cantidad de cada item para obtener el total de items
function cantidadTotalItems() {
    return carrito.reduce((sum, item) => sum + item.cantidad, 0);
}

// Función para limpiar el carrito, vaciamos el array del carrito, actualizamos el localStorage y la interfaz del carrito
function limpiarCarrito() {
    carrito = [];
    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarBadgeCarrito();
    renderizarOffcanvas();
}

// Función para actualizar el badge del carrito, mostramos la cantidad total de items en el badge y lo ocultamos si el carrito está vacío
function actualizarBadgeCarrito() {
    const badge = document.getElementById('cart-badge');
    if (!badge) return; // Si no encontramos el badge, no hacemos nada
    const total = cantidadTotalItems();
    badge.textContent = total; // Actualizamos el texto del badge con la cantidad total de items en el carrito
    badge.style.display = total > 0 ? 'flex' : 'none'; // Mostramos el badge solo si hay items en el carrito, si no, lo ocultamos
}

/*
Función para renderizar el offcanvas con los items del carrito, esta función se encarga de mostrar los items del carrito en el offcanvas, 
si el carrito está vacío muestra un mensaje indicando que el carrito está vacío, 
y si hay items muestra cada item con su información y opciones para cambiar la cantidad o eliminarlo 
*/
function renderizarOffcanvas() {
    const contenedor = document.getElementById('cart-items');
    const vacio = document.getElementById('cart-empty');
    const footer = document.getElementById('cart-footer');
    if (!contenedor) return;

    // Si el carrito está vacío, mostramos el mensaje de carrito vacío y ocultamos el footer con el total y el botón de checkout
    if (carrito.length === 0) {
        contenedor.innerHTML = '';
        if (vacio) vacio.classList.remove('d-none');
        if (footer) footer.classList.add('d-none');
        return;
    }

    // Si el carrito tiene items, mostramos cada item con su información y opciones para cambiar la cantidad o eliminarlo, ocultamos el mensaje de carrito vacío y mostramos el footer con el total y el botón de checkout
    if (vacio) vacio.classList.add('d-none');
    if (footer) footer.classList.remove('d-none');

    contenedor.innerHTML = carrito.map(item => `
        <div class="cart-item">
            <div class="d-flex gap-3 align-items-start">
                <img src="${item.imagen}" alt="${item.nombre}"
                     class="rounded-3" style="width:70px;height:70px;object-fit:cover;">
                <div class="flex-grow-1 min-w-0">
                    <h6 class="fw-bold mb-1 text-truncate">${item.nombre}</h6>
                    <p class="text-muted small mb-2">${item.color ? `<span class="me-2">Color: <strong>${item.color}</strong></span>` : ''}Talla: <strong>${item.talla}</strong></p>
                    <div class="d-flex align-items-center gap-2">
                        <button class="btn btn-sm btn-outline-secondary rounded-circle p-1 lh-1"
                                onclick="cambiarCantidad('${item.key}', -1)" style="width:28px;height:28px;">
                            <span class="material-symbols-outlined fs-6">remove</span>
                        </button>
                        <span class="fw-semibold" style="min-width:24px;text-align:center;">${item.cantidad}</span>
                        <button class="btn btn-sm btn-outline-secondary rounded-circle p-1 lh-1"
                                onclick="cambiarCantidad('${item.key}', 1)" style="width:28px;height:28px;">
                            <span class="material-symbols-outlined fs-6">add</span>
                        </button>
                        <span class="ms-auto fw-bold span-precio small">$${(item.precio * item.cantidad).toFixed(0)}</span>
                        <button class="btn btn-sm text-danger p-0 border-0"
                                onclick="eliminarDelCarrito('${item.key}')" title="Eliminar">
                            <span class="material-symbols-outlined fs-5">delete</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    const totalEl = document.getElementById('cart-total');
    if (totalEl) totalEl.textContent = `$${calcularTotal().toFixed(0)} MXN`; // Actualizamos el total en el footer del carrito
}

/*
Función para limpiar el carrito después de realizar el checkout, 
esta función se puede llamar después de que el usuario complete el proceso de compra para vaciar el carrito y actualizar la interfaz
*/
function limpiarCarritoDespuesCheckout() {
    limpiarCarrito();
}

document.addEventListener('DOMContentLoaded', function () {
    actualizarBadgeCarrito();
    renderizarOffcanvas();

    // Re-render cuando se abre el offcanvas
    const offcanvasEl = document.getElementById('offcanvasCarrito');
    if (offcanvasEl) {
        offcanvasEl.addEventListener('show.bs.offcanvas', function () {
            renderizarOffcanvas();
        });
    }
});
