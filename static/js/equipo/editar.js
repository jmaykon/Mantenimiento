<div id="modal-editar" 
     x-data="{ show: false }" 
     x-init="setTimeout(() => show = true, 50)"
     @equipo-actualizado.window="show = false; setTimeout(() => $el.remove(), 400)"
     class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-md"
     x-show="show">

    <div class="bg-white rounded-[2.5rem] w-full max-w-4xl shadow-2xl relative max-h-[90vh] flex flex-col overflow-hidden">
        <div class="p-8 border-b border-slate-100 flex justify-between items-center">
            <h2 class="text-3xl font-black text-slate-800">Editar {{ equipo.serial }}</h2>
            <button @click="show = false; setTimeout(() => $el.closest('#modal-editar').remove(), 400)" class="text-slate-400 font-bold">✕</button>
        </div>

        <form hx-post="{% url 'equipo:editar_equipo' equipo.id_equipo %}" 
              class="flex-1 overflow-y-auto p-8 space-y-8">
            {% csrf_token %}
            
            <input type="hidden" name="serial" value="{{ equipo.serial }}">
            <input type="hidden" name="aec" value="{{ equipo.aec }}">

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label class="font-bold text-xs text-slate-500 uppercase">Dirección IP</label>
                    <input type="text" name="ip" value="{{ equipo.ip|default:'' }}" class="w-full p-3 rounded-xl border border-slate-200">
                </div>
                <div>
                    <label class="font-bold text-xs text-slate-500 uppercase">Estado</label>
                    <select name="estado_equipo" class="w-full p-3 rounded-xl border border-slate-200">
                        <option value="ACTIVO" {% if equipo.estado_equipo == 'ACTIVO' %}selected{% endif %}>ACTIVO</option>
                        <option value="MANTENIMIENTO" {% if equipo.estado_equipo == 'MANTENIMIENTO' %}selected{% endif %}>MANTENIMIENTO</option>
                    </select>
                </div>
            </div>

            <div class="flex justify-end gap-3 pt-4">
                <button type="button" @click="show = false" class="px-6 py-2 text-slate-500 font-bold">Cancelar</button>
                <button type="submit" class="bg-indigo-600 text-white px-10 py-3 rounded-xl font-bold">Guardar Cambios</button>
            </div>
        </form>
    </div>
</div>