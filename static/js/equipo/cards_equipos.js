document.addEventListener('htmx:confirm', function(evt) {
    // Solo actuamos si el elemento tiene el atributo hx-confirm
    if (evt.detail.question) {
        evt.preventDefault(); // Detenemos el envío automático de HTMX

        Swal.fire({
            title: '¿Estás seguro?',
            text: evt.detail.question,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#4f46e5', // Indigo 600
            cancelButtonColor: '#f43f5e',  // Rose 500
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Cancelar',
            background: '#ffffff',
            borderRadius: '2rem',
            customClass: {
                popup: 'rounded-[2rem] shadow-2xl border border-slate-100',
                confirmButton: 'rounded-xl px-6 py-3 font-bold',
                cancelButton: 'rounded-xl px-6 py-3 font-bold'
            }
        }).then((result) => {
            if (result.isConfirmed) {
                // Si el usuario confirma, reanudamos la petición de HTMX
                evt.detail.issueRequest(true);
            }
        });
    }
});