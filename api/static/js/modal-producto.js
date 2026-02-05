document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal-trigger').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();

            const stock = parseInt(this.dataset.stock) || 0;
            const productoId = this.dataset.productoId;

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

            // Aqui obteneremos el id del producto que se clickeo
            document.getElementById('modalProductoId').value = productoId;

            // Aqui hacemos la accion del formulario de resena con el id del producto para guardar la resena
            document.getElementById('formResena').action = `/producto/${productoId}/resena/`;

            // 👇 LOGIN CHECK (esto SÍ funciona en JS)
            const formResena = document.getElementById('formResena');
            const loginRequerido = document.getElementById('loginRequerido');

            // Y cambia el if por esto temporalmente:
            if (window.USER_LOGGED_IN === true || window.USER_LOGGED_IN === 'true') {
                console.log('MOSTRANDO formulario');
                document.getElementById('formResena').style.display = 'block';
                document.getElementById('loginRequerido').style.display = 'none';
            } else {
                console.log('MOSTRANDO mensaje login');
                document.getElementById('formResena').style.display = 'none';
                document.getElementById('loginRequerido').style.display = 'block';
            }


            new bootstrap.Modal(document.getElementById('modalProducto')).show();
        });
    });
});
