
const modal = document.getElementById('modal-aprobar');
const openBtn = document.getElementById('openModalBtn');
const closeBtn = document.getElementById('closeModalBtn');
const approveBtn = document.getElementById('approveBtn');

// Abrir modal
openBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
});

// Cerrar modal
closeBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
});

// Aprobar
approveBtn.addEventListener('click', () => {
    alert('Ticket aprobado ✔️');
    modal.classList.add('hidden');
});

// Cerrar haciendo click fuera
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.add('hidden');
    }
});

