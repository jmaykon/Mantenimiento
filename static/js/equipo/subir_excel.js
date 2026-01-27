/**
 * Gestión de Importación Masiva de Equipos vía Excel
 */

// 1. Funciones Globales para Control de UI (Modales)
window.openModalSubirExcel = function() {
    const modal = document.getElementById('modal-subir-excel');
    const content = document.getElementById('modal-content-excel');
    if (modal && content) {
        modal.classList.remove('opacity-0', 'pointer-events-none');
        content.classList.remove('scale-90');
        // Resetear estado del formulario al abrir
        document.getElementById('form-subir-excel').reset();
        document.getElementById('status-excel').classList.add('hidden');
    }
};

window.cerrarModalSubirExcel = function() {
    const modal = document.getElementById('modal-subir-excel');
    const content = document.getElementById('modal-content-excel');
    if (modal && content) {
        modal.classList.add('opacity-0', 'pointer-events-none');
        content.classList.add('scale-90');
    }
};

// 2. Lógica de Envío de Formulario
document.addEventListener('DOMContentLoaded', function() {
    const formExcel = document.getElementById('form-subir-excel');
    const statusDiv = document.getElementById('status-excel');
    const btnSubmit = document.getElementById('btn-submit-excel');

    if (formExcel) {
        formExcel.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Preparar FormData
            const formData = new FormData(this);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // UI: Bloquear botón y mostrar carga
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg> Procesando archivo...
            `;

            statusDiv.classList.remove('hidden');
            statusDiv.className = "mt-4 p-3 rounded-lg text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100";
            statusDiv.innerText = "Estamos validando y guardando los datos del Excel. No cierres esta ventana.";

            try {
                // El URL debe coincidir con el nombre en tu urls.py (ej: 'equipo:importar_excel')
                // Si no usas Django template tags en JS, pon la ruta manual: '/equipo/importar-excel/'
                const response = await fetch('/equipo/importar-excel/', { 
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    // Éxito
                    statusDiv.className = "mt-4 p-3 rounded-lg text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-100";
                    statusDiv.innerHTML = "✅ <strong>¡Importación exitosa!</strong> Los equipos han sido añadidos. Recargando inventario...";
                    
                    // Recargar página para mostrar la lista y los mensajes de sesión
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);

                } else {
                    // Error reportado por el servidor
                    throw new Error(data.message || "Error desconocido al procesar el Excel.");
                }

            } catch (error) {
                // Manejo de errores (conexión, duplicados, etc.)
                console.error("Error en Importación:", error);
                statusDiv.className = "mt-4 p-3 rounded-lg text-xs font-medium bg-rose-50 text-rose-700 border border-rose-100";
                statusDiv.innerHTML = `❌ <strong>Error:</strong> ${error.message}`;
                
                // Reactivar botón para reintentar
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = "🚀 Subir e Importar";
            }
        });
    }
});