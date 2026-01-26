// Estado global de los componentes dinámicos
let rams = [];
let discos = [];
let isEditing = false;

/**
 * Abre el modal y bloquea el scroll del body
 */
window.openModal = function (editMode = false) {
    isEditing = editMode;
    const modal = document.getElementById('modalNuevoEquipo');

    // Textos dinámicos
    document.getElementById('modalTitle').innerText = isEditing ? 'Editar Registro TI' : 'Nuevo Activo TI';
    document.getElementById('btnSave').innerText = isEditing ? 'Actualizar Información' : 'Guardar en Inventario';

    // Mostrar modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    // Bloquear scroll de la página principal para evitar el "doble scroll"
    document.body.style.overflow = 'hidden';
};

/**
 * Cierra el modal y limpia el formulario
 */
window.closeModal = function () {
    const modal = document.getElementById('modalNuevoEquipo');
    modal.classList.add('hidden');
    modal.classList.remove('flex');

    // Restaurar scroll
    document.body.style.overflow = 'auto';
    resetForm();
};

/**
 * Gestión de filas de RAM
 */
window.addRamRow = function () {
    rams.push({ capacidad: '', tipo: '', frecuencia: '' });
    renderRams();
};

window.removeRam = function (index) {
    rams.splice(index, 1);
    renderRams();
};

function renderRams() {
    const container = document.getElementById('ramContainer');
    if (!container) return;
    container.innerHTML = rams.map((r, i) => `
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-indigo-100 animate-in fade-in zoom-in duration-200">
            <div class="grid grid-cols-3 gap-2 mb-3">
                <input value="${r.capacidad}" oninput="rams[${i}].capacidad=this.value" placeholder="16GB" class="w-full p-2 text-xs border rounded-lg outline-none focus:border-indigo-400">
                <input value="${r.tipo}" oninput="rams[${i}].tipo=this.value" placeholder="DDR4" class="w-full p-2 text-xs border rounded-lg outline-none focus:border-indigo-400">
                <button type="button" onclick="removeRam(${i})" class="text-rose-500 text-[10px] font-black uppercase hover:bg-rose-50 rounded-lg">Eliminar</button>
            </div>
            <input value="${r.frecuencia}" oninput="rams[${i}].frecuencia=this.value" placeholder="Frecuencia (Ej: 3200MHz)" class="w-full p-2 text-xs border rounded-lg outline-none focus:border-indigo-400">
        </div>
    `).join('');
}

/**
 * Gestión de filas de Discos
 */
window.addDiscoRow = function () {
    discos.push({ tipo: '', capacidad: '' });
    renderDiscos();
};

window.removeDisco = function (index) {
    discos.splice(index, 1);
    renderDiscos();
};

function renderDiscos() {
    const container = document.getElementById('discoContainer');
    if (!container) return;
    container.innerHTML = discos.map((d, i) => `
        <div class="grid grid-cols-2 gap-3 bg-white p-4 rounded-2xl shadow-sm border border-emerald-100 animate-in fade-in zoom-in duration-200">
            <input value="${d.tipo}" oninput="discos[${i}].tipo=this.value" placeholder="SSD / NVMe" class="w-full p-2 text-xs border rounded-lg outline-none focus:border-emerald-400">
            <input value="${d.capacidad}" oninput="discos[${i}].capacidad=this.value" placeholder="512GB" class="w-full p-2 text-xs border rounded-lg outline-none focus:border-emerald-400">
            <button type="button" onclick="removeDisco(${i})" class="text-rose-500 text-[10px] font-black uppercase col-span-2 text-center py-1 hover:bg-rose-50 rounded-lg mt-1 border border-dashed border-rose-200">Eliminar Unidad</button>
        </div>
    `).join('');
}

/**
 * Captura de datos
 */
window.saveData = async function () {
    // 1. Recolectar datos con los IDs exactos del HTML
    const data = {
        tipo: document.getElementById('pcTipo').value,
        aec: document.getElementById('pcAec').value,
        so: document.getElementById('pcSO').value, // En el HTML usaste id="pcSO"
        ip: document.getElementById('pcIp').value,
        marca: document.getElementById('pcMarca').value,
        modelo: document.getElementById('pcModelo').value,
        procesador: document.getElementById('pcProcesador').value,
        serial: document.getElementById('pcSerial').value,
        estado: document.getElementById('pcEstado').value,
        lugar_id: document.getElementById('id_lugar').value,
        user_id: document.getElementById('id_users').value,
        observaciones: document.getElementById('pcObservaciones_equipo').value,
        rams: rams,   // Arreglo global
        discos: discos // Arreglo global
    };

    // Validación básica
    if (!data.serial || !data.tipo) {
        alert("Por favor completa el Serial y el Tipo de Hardware.");
        return;
    }

    try {
        const response = await fetch('/equipo/guardar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // CAMBIA LA LÍNEA DEL TOKEN POR ESTA:
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            closeModal();
            alert("✅ Guardado: " + result.message);
            document.body.dispatchEvent(new Event('update-list'));
        } else {
            console.error("Errores del formulario:", result.errors);
            alert("❌ Error: " + (result.message || "Revisa los campos del formulario"));
        }
    } catch (error) {
        console.error("Error en la conexión:", error);
        alert("Fallo de comunicación con el servidor.");
    }
};

// Función auxiliar para recuperar el token CSRF (Obligatorio en Django para POST)
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




function resetForm() {
    document.getElementById('pcTipo').value = "";
    document.getElementById('pcAec').value = "";
    document.getElementById('pcIp').value = "";
    rams = [];
    discos = [];
    renderRams();
    renderDiscos();
}

document.body.addEventListener('htmx:beforeSwap', function (evt) {
    if (!evt.detail.target) {
        console.error("HTMX: ¡El target no existe!", evt.detail);
    }
});
