document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal-trigger').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();

            const stock = parseInt(this.dataset.stock) || 0;

            // Datos básicos
            document.getElementById('modalImagen').src = this.dataset.imagen;
            document.getElementById('modalTitulo').textContent = this.dataset.titulo;
            document.getElementById('modalPrecio').textContent = this.dataset.precio;
            document.getElementById('modalCategoria').textContent = this.dataset.categoria || 'Sin categoría';
            
            // NUEVOS DATOS - ESTO ES LO QUE FALTABA
            document.getElementById('modalTallas').textContent = this.dataset.tallas || 'N/A';
            document.getElementById('modalMateriales').textContent = this.dataset.materiales || 'N/A';
            document.getElementById('modalCuidados').textContent = this.dataset.cuidados || 'N/A';
            
            document.getElementById('modalDescripcion').textContent = this.dataset.descripcion || '';


            // Stock
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
            // Aqui obteneremos el id del producto que se clickeo
            document.getElementById('modalProductoId').value = productoId;
            // Aqui hacemos la accion del formulario de resena con el id del producto para guardar la resena
            document.getElementById('formResena').action = `/producto/${productoId}/resena/`;

            // Creamos variables constantes para pasarle los modales de resena y login
            const formResena = document.getElementById('formResena');
            const loginRequerido = document.getElementById('loginRequerido');

            // Mostrar el formulario de resena si el usuario esta logueado
            if (window.USER_LOGGED_IN === true || window.USER_LOGGED_IN === 'true') {
                console.log('MOSTRANDO formulario');
                formResena.style.display = 'block'; // Mostramos el formulario
                loginRequerido.style.display = 'none'; // No mostramos el mensaje
                // De los contrario no lo mostramos
            } else {
                console.log('MOSTRANDO mensaje login');
                formResena.style.display = 'none'; // No mostramos el formulario
                loginRequerido.style.display = 'block'; // Mostramos el mensaje que necesita loguearse
            }

            console.log('ANTES modal - action:', formResena.action);
            formResena.action = `/producto/${productoId}/resena/`;
            console.log('DESPUÉS set - action:', formResena.action);
            console.log('FINAL - action:', formResena.action);

            new bootstrap.Modal(document.getElementById('modalProducto')).show();
        });
    });

    // ✅ UX MÍNIMA: Solo loading state
    const formResena = document.getElementById('formResena');
    if (formResena) {
        console.log('productoId:', document.querySelector('.modal-trigger').dataset.productoId);
console.log('Form action:', document.getElementById('formResena').action);

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


