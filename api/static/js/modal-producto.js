document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal-trigger').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();

            // Datos del producto
            const stock = parseInt(this.dataset.stock) || 0; // Convertir a número o 0 si no es un número
            
            document.getElementById('modalImagen').src = this.dataset.imagen;
            document.getElementById('modalTitulo').textContent = this.dataset.titulo;
            document.getElementById('modalPrecio').textContent = this.dataset.precio;
            document.getElementById('modalCategoria').textContent = this.dataset.categoria;
            document.getElementById('modalDescripcion').textContent = this.dataset.descripcion;
            
            // STOCK DINAMICO, les pasamos los nombres de los IDS del HTML base
            const stockIcon = document.getElementById('modalStockIcon');
            const stockText = document.getElementById('modalStockText');
            
            if (stock > 0) { // Si hay stock entonces es verde
                stockIcon.style.backgroundColor = '#10b981';
                stockText.textContent = `Disponible (${stock} unidades)`;
                stockText.className = 'text-success fw-medium small';
            } else { // Si no hay stock entonces es rojo
                stockIcon.style.backgroundColor = '#ef4444'; 
                stockText.textContent = 'Agotado';
                stockText.className = 'text-danger fw-medium small';
            }

            new bootstrap.Modal(document.getElementById('modalProducto')).show(); // Mostrar el modal
        });
    });
});
