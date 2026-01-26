/**
 * Lógica para la edición de Activos TI
 */

// Función para agregar filas dinámicas (RAM/Disco)
function SafeAddRow(tipo, cap = '', det = '', freq = '') {
    const container = document.getElementById(tipo + '-container-edit');
    if (!container) return;

    const div = document.createElement('div');
    div.className = "flex gap-2 bg-white p-2 rounded-xl shadow-sm border border-slate-100 animate-in slide-in-from-top-1";
    
    if (tipo === 'ram') {
        div.innerHTML = `
            <input type="text" name="ram_capacidad[]" value="${cap}" placeholder="Cap" class="w-1/4 text-[11px] font-bold p-2 bg-slate-50 rounded-lg border-none">
            <input type="text" name="ram_tipo[]" value="${det}" placeholder="Tipo" class="w-1/4 text-[11px] font-bold p-2 bg-slate-50 rounded-lg border-none">
            <input type="text" name="ram_frecuencia[]" value="${freq}" placeholder="MHz" class="w-1/4 text-[11px] font-bold p-2 bg-slate-50 rounded-lg border-none">
            <button type="button" onclick="this.parentElement.remove()" class="text-rose-400 px-2 font-bold hover:text-rose-600">✕</button>
        `;
    } else {
        div.innerHTML = `
            <input type="text" name="disco_capacidad[]" value="${cap}" placeholder="Cap" class="w-1/3 text-[11px] font-bold p-2 bg-slate-50 rounded-lg border-none">
            <input type="text" name="disco_tipo[]" value="${det}" placeholder="Tipo" class="w-2/3 text-[11px] font-bold p-2 bg-slate-50 rounded-lg border-none">
            <button type="button" onclick="this.parentElement.remove()" class="text-rose-400 px-2 font-bold hover:text-rose-600">✕</button>
        `;
    }
    container.appendChild(div);
}

// Confirmación con SweetAlert2 antes de enviar con HTMX
function ConfirmarActualizacion() {
    Swal.fire({
        title: '¿Guardar cambios?',
        text: "Se actualizará la ficha técnica del activo.",
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#4f46e5',
        cancelButtonColor: '#f43f5e',
        confirmButtonText: 'Sí, actualizar',
        cancelButtonText: 'Cancelar',
        customClass: { popup: 'rounded-[2.5rem]' }
    }).then((result) => {
        if (result.isConfirmed) {
            htmx.trigger("#form-editar-equipo", "submit");
        }
    });
}

// Listener global para cerrar modal y mostrar éxito tras HTMX
document.body.addEventListener('htmx:afterOnLoad', function(evt) {
    if (evt.detail.elt.id === 'form-editar-equipo') {
        document.getElementById('modal-editar-equipo')?.remove();
        Swal.fire({
            title: '¡Sincronizado!',
            text: 'Activo actualizado con éxito.',
            icon: 'success',
            timer: 2000,
            showConfirmButton: false,
            customClass: { popup: 'rounded-[2.5rem]' }
        });
    }
});