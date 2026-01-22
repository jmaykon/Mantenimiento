// Cerramos el modal después de agregar
closeModal('addComponenteModal');

// Añadimos la nueva fila a la tabla
let table = document.querySelector('#tablaComponentes tbody');
if (table) {
    table.insertAdjacentHTML('beforeend', '{{ comp|safe }}');
}




/* Animación bonita para modal */
@keyframes slide - down {
    0 % { transform: translateY(-20px); opacity: 0; }
    100 % { transform: translateY(0); opacity: 1; }
}
.animate - slide - down {
    animation: slide - down 0.3s ease - out forwards;
}

