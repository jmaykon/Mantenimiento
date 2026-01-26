/**
 * GESTIÓN DE MODAL PARA IMPORTACIÓN DE EXCEL
 */

// Usamos window para asegurar que las funciones sean globales y accesibles desde el HTML
window.openModalSubirExcel = function() {
    const modal = document.getElementById('modal-subir-excel');
    const content = document.getElementById('modal-content-excel');

    if (modal) {
        modal.classList.remove('opacity-0', 'pointer-events-none');
        modal.classList.add('opacity-100', 'pointer-events-auto');
        if (content) {
            content.classList.remove('scale-90');
            content.classList.add('scale-100');
        }
    }
};

window.cerrarModalSubirExcel = function() {
    const modal = document.getElementById('modal-subir-excel');
    const content = document.getElementById('modal-content-excel');

    if (modal) {
        modal.classList.add('opacity-0', 'pointer-events-none');
        modal.classList.remove('opacity-100', 'pointer-events-auto');
        if (content) {
            content.classList.add('scale-90');
            content.classList.remove('scale-100');
        }
    }
};

// Cerrar modal al hacer clic en el fondo oscuro
document.addEventListener('DOMContentLoaded', () => {
    const btnSave = document.getElementById('btnSave');
    // Si btnSave no existe en esta página específica, no intentes ponerle un listener
    if (btnSave) {
        btnSave.addEventListener('click', saveData);
    }
});