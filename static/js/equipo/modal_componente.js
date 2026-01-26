/**
 * Lógica para el Modal de Stock de Periféricos vinculada al modelo Componente
 */

function abrirModalStock() {
    const modal = document.getElementById('modalStock');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
    }
}

function cerrarModalStock() {
    const modal = document.getElementById('modalStock');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = 'auto';

        // Limpiar todos los campos nuevos
        const ids = ['periTipo', 'periAec', 'periMarca', 'periModelo', 'periSerial', 'periObs'];
        ids.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
    }
}

async function addGlobalComp() {
    // Captura de datos siguiendo el modelo Django
    const data = {
        tipo: document.getElementById('periTipo').value.trim(),
        aec: document.getElementById('periAec').value.trim(),
        marca: document.getElementById('periMarca').value.trim(),
        modelo: document.getElementById('periModelo').value.trim(),
        serial: document.getElementById('periSerial').value.trim(),
        observaciones: document.getElementById('periObs').value.trim(),
        estado: 'ACTIVO' // Valor por defecto del modelo
    };

    // Validación de campos obligatorios según tu modelo
    if (!data.tipo || !data.aec || !data.serial) {
        alert("Tipo, AEC y Serial son obligatorios.");
        return;
    }

    console.log("Datos para el modelo Componente:", data);

    try {
        const btn = document.querySelector('#modalStock .btn-gradient') || document.querySelector('#modalStock button[onclick^="addGlobalComp"]');
        btn.disabled = true;
        btn.innerHTML = "Guardando...";

        // Simulación de envío
        setTimeout(() => {
            alert("¡Componente registrado en stock correctamente!");
            btn.disabled = false;
            btn.innerHTML = "Añadir al Stock";
            cerrarModalStock();
        }, 800);

    } catch (error) {
        console.error("Error:", error);
        alert("Error al procesar el registro.");
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') cerrarModalStock();
});