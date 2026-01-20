// modal_aprobar.js
const modalAprobar = document.getElementById('modal-aprobar');
const approveBtn = document.getElementById('approveBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
let currentTicketId = null;

// Event delegation: escucha clicks en todo el contenedor de tickets
document.getElementById('tickets-container').addEventListener('click', (e) => {
    const btn = e.target.closest('.openModalBtn');
    if (!btn) return;

    currentTicketId = btn.dataset.ticketId;

    // Abrir modal
    modalAprobar.classList.remove('hidden');
    modalAprobar.classList.add('flex');

    // Cargar datos del ticket
    fetch(`/mantenimiento/ticket-datos/${currentTicketId}/`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            document.getElementById('modal-ticket-id').innerText = data.id_ticket;
            document.getElementById('modal-diagnostico').innerText = data.diagnostico || '-';
            document.getElementById('modal-observaciones').innerText = data.observaciones_tecnicas || '-';
            document.getElementById('modal-solucion').innerText = data.solucion_aplicada || '-';
            document.getElementById('modal-descripcion').innerText = data.descripcion || '-';

            // Botón aprobar
            if (data.aprobado == 1) {
                approveBtn.disabled = true;
                approveBtn.innerText = 'Aprobado';
                approveBtn.classList.add('bg-gray-500', 'cursor-not-allowed');
                approveBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
            } else {
                approveBtn.disabled = false;
                approveBtn.innerText = 'Aprobar';
                approveBtn.classList.remove('bg-gray-500', 'cursor-not-allowed');
                approveBtn.classList.add('bg-green-600');
            }
        })
        .catch(error => {
            console.error('Error cargando datos del ticket:', error);
            alert('No se pudo cargar la información del ticket.');
        });
});

// Cerrar modal
closeModalBtn.addEventListener('click', () => {
    modalAprobar.classList.add('hidden');
    modalAprobar.classList.remove('flex');
});

// Botón Aprobar
approveBtn.addEventListener('click', () => {
    if (!currentTicketId) return;

    // Confirmación con SweetAlert
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Una vez aprobado, no podrás deshacer esta acción.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, Aprobar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            // Llamada fetch para aprobar
            fetch(`/mantenimiento/aprobar-ticket/${currentTicketId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        const ticketDiv = document.getElementById(`ticket-${currentTicketId}`);
                        const btn = ticketDiv.querySelector('.openModalBtn');
                        btn.disabled = true;
                        btn.innerText = 'Aprobado';
                        btn.classList.add('bg-gray-400', 'cursor-not-allowed');
                        btn.classList.remove('bg-yellow-600', 'hover:bg-yellow-700');

                        modalAprobar.classList.add('hidden');
                        modalAprobar.classList.remove('flex');

                        // Feedback de SweetAlert
                        Swal.fire(
                            '¡Aprobado!',
                            'El ticket ha sido aprobado correctamente.',
                            'success'
                        );
                    } else {
                        Swal.fire('Error', 'No se pudo aprobar el ticket.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error al aprobar el ticket:', error);
                    Swal.fire('Error', 'No se pudo aprobar el ticket.', 'error');
                });
        }
    });
});


// Función para obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
