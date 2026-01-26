// Manejador de eventos HTMX
document.body.addEventListener('htmx:afterOnLoad', function(evt) {
    // Si el target es el contenedor de nuevo equipo, mostramos el modal
    if (evt.detail.target.id === "contenido-nuevo-equipo") {
        const modal = document.getElementById('modalNuevoEquipo');
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
    
    // Si el target es el stock
    if (evt.detail.target.id === "contenido-stock") {
        const modal = document.getElementById('modalStock');
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
});

// Funciones para cerrar
function cerrarModalNuevo() {
    const modal = document.getElementById('modalNuevoEquipo');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.getElementById('contenido-nuevo-equipo').innerHTML = ""; // Limpiar
}

function cerrarModalStock() {
    const modal = document.getElementById('modalStock');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// Cerrar con tecla ESC
document.addEventListener('keydown', (e) => {
    if (e.key === "Escape") {
        cerrarModalNuevo();
        cerrarModalStock();
    }
});