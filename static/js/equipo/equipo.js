function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (!modal) {
        console.warn(`Modal ${id} no existe`);
        return;
    }
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}
