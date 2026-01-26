// Estado de la aplicación
window.state = window.state || {
    pcs: [
        {
            id: 1,
            tipo: 'Laptop',
            marca: 'Dell',
            modelo: 'Latitude 5420',
            serial: 'ABC1234',
            aec: 'AEC-1001',
            estado_equipo: 'ACTIVO',
            ip: '192.168.1.50',
            procesador: 'Core i7-1185G7',
            sistema_operativo: 'Windows 11 Pro',
            ramData: [{ capacidad: '16GB', tipo: 'DDR4', frecuencia: '3200MHz' }],
            discos: [{ tipo: 'SSD NVMe', capacidad: '512GB', estado: 'NUEVO' }],
            componentes: [{ tipo: 'Mouse', marca: 'Logitech', serial: 'M-990' }],
            open: false // Para el acordeón
        }
    ],
    componentesGlobales: [
        { id: 101, tipo: 'Teclado', marca: 'HP', aec: 'AEC-PER-01' }
    ]
};



// Función Principal de Renderizado
function renderApp() {
    renderGlobalStock();
    renderPCs();
}

// Renderiza el stock superior
function renderGlobalStock() {
    const grid = document.getElementById('global-components-grid');
    const countBadge = document.getElementById('global-stock-count');

    countBadge.textContent = `${state.componentesGlobales.length} Disponibles`;

    if (state.componentesGlobales.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-10 border-4 border-dashed border-slate-200 rounded-[2rem] flex flex-col items-center justify-center text-slate-400 bg-white/40">
                <p class="text-sm font-bold tracking-widest uppercase opacity-60">No hay periféricos libres</p>
            </div>`;
        return;
    }

    grid.innerHTML = state.componentesGlobales.map((comp, index) => `
        <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm flex justify-between items-center group hover:border-indigo-300 hover:shadow-md transition-all">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-50 to-indigo-50 flex items-center justify-center text-lg border border-slate-100">🖱️</div>
                <div>
                    <p class="font-bold text-slate-800 text-sm">${comp.tipo}</p>
                    <p class="text-[10px] text-indigo-500 font-bold uppercase tracking-tighter">${comp.marca} • ${comp.aec}</p>
                </div>
            </div>
            <button onclick="deleteGlobal(${index})" class="opacity-0 group-hover:opacity-100 p-2 text-slate-300 hover:text-rose-500 transition-all">✕</button>
        </div>
    `).join('');
}

// Renderiza las tarjetas de PC
function renderPCs() {
    const container = document.getElementById('pc-container');

    container.innerHTML = state.pcs.map((pc, index) => {
        const statusClass = {
            'ACTIVO': 'bg-emerald-50 text-emerald-600 border-emerald-200',
            'MANTENIMIENTO': 'bg-amber-50 text-amber-600 border-amber-200',
            'INACTIVO': 'bg-rose-50 text-rose-600 border-rose-200'
        }[pc.estado_equipo];

        return `
        <div class="bg-white rounded-[2rem] border border-slate-200 shadow-sm overflow-hidden transition-all hover:shadow-xl group/card">
            <div class="p-5 flex flex-wrap justify-between items-center gap-4 cursor-pointer hover:bg-slate-50/50" onclick="togglePC(${index})">
                <div class="flex items-center gap-4">
                    <div class="${pc.tipo === 'Laptop' ? 'bg-gradient-to-br from-amber-400 to-orange-500' : 'bg-gradient-to-br from-indigo-500 to-violet-600'} w-14 h-14 rounded-2xl flex items-center justify-center text-2xl shadow-lg text-white">
                        ${pc.tipo === 'Laptop' ? '💻' : '🖥️'}
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="font-black text-slate-800 text-lg leading-tight">${pc.marca} ${pc.modelo}</h3>
                            <span class="status-badge ${statusClass}">${pc.estado_equipo}</span>
                        </div>
                        <p class="text-xs text-slate-400 font-bold uppercase tracking-wider">S/N: ${pc.serial} • AEC: ${pc.aec}</p>
                    </div>
                </div>

                <div class="flex items-center gap-4 bg-indigo-50/50 px-5 py-3 rounded-2xl border border-white">
                    <div class="text-right">
                        <p class="text-[9px] font-black text-indigo-400 uppercase tracking-widest">Dirección IP</p>
                        <p class="text-sm font-mono font-black text-indigo-600">${pc.ip || '0.0.0.0'}</p>
                    </div>
                    <div class="h-8 w-px bg-indigo-200"></div>
                    <div class="flex gap-1">
                        <button onclick="event.stopPropagation(); editPC(${index})" class="p-2.5 bg-white hover:bg-indigo-600 hover:text-white rounded-xl transition-all text-indigo-400 border border-indigo-100">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                        </button>
                    </div>
                </div>
            </div>

            <div class="${pc.open ? 'block' : 'hidden'} bg-gradient-to-b from-slate-50 to-white border-t border-slate-100">
                <div class="p-8">
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <div class="space-y-4">
                            <h4 class="text-[10px] font-black text-indigo-300 uppercase tracking-[0.2em]">Sistema Base</h4>
                            <div class="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm text-xs">
                                <div class="flex justify-between py-2 border-b border-slate-50">
                                    <span class="text-slate-400 font-bold">Procesador</span>
                                    <span class="font-black text-slate-700">${pc.procesador}</span>
                                </div>
                                <div class="flex justify-between py-2">
                                    <span class="text-slate-400 font-bold">OS</span>
                                    <span class="font-black text-indigo-600">${pc.sistema_operativo}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="space-y-4">
                            <h4 class="text-[10px] font-black text-indigo-300 uppercase tracking-[0.2em]">Memoria RAM</h4>
                            <div class="flex gap-3">
                                ${pc.ramData.map(r => `
                                    <div class="bg-gradient-to-br from-indigo-600 to-violet-700 text-white p-4 rounded-2xl flex-1 shadow-md">
                                        <p class="text-2xl font-black">${r.capacidad}</p>
                                        <p class="text-[10px] opacity-80 uppercase font-bold">${r.tipo} • ${r.frecuencia}</p>
                                    </div>
                                `).join('')}
                            </div>
                        </div>

                        <div class="space-y-4">
                            <h4 class="text-[10px] font-black text-indigo-300 uppercase tracking-[0.2em]">Almacenamiento</h4>
                            ${pc.discos.map(d => `
                                <div class="bg-white p-4 rounded-2xl border border-slate-100 flex items-center gap-4">
                                    <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-500 flex items-center justify-center border border-emerald-100">💾</div>
                                    <div>
                                        <p class="text-xs font-black text-slate-700 uppercase">${d.tipo} ${d.capacidad}</p>
                                        <p class="text-[9px] font-bold text-emerald-500 uppercase">${d.estado}</p>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

// --- FUNCIONES DE ACCIÓN ---

window.togglePC = (index) => {
    state.pcs[index].open = !state.pcs[index].open;
    renderPCs();
};

window.deleteGlobal = (index) => {
    Swal.fire({
        title: '¿Eliminar periférico?',
        text: "Esta acción no se puede deshacer",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#4f46e5',
        confirmButtonText: 'Sí, eliminar'
    }).then((result) => {
        if (result.isConfirmed) {
            state.componentesGlobales.splice(index, 1);
            renderApp();
        }
    });
};

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('pc-container')) {
        renderApp();
    }
});



