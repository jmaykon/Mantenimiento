document.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-confirm-delete]');
    if (!btn) return;

    e.preventDefault();

    Swal.fire({
        title: '¿Eliminar equipo?',
        text: 'Esta acción no se puede deshacer',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#4f46e5',
        cancelButtonColor: '#f43f5e',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            htmx.trigger(btn, 'confirmado');
        }
    });
});

// Relanza HTMX
document.addEventListener('confirmado', function (e) {
    htmx.process(e.target);
});
