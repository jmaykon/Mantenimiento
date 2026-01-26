document.addEventListener('alpine:init', () => {
    Alpine.data('pcDashboard', () => ({
        pcs: [],
        componentesGlobales: [],
        openAddPC: false,
        openAddComponent: false,
        openAddComponentGlobal: false,
        isEditing: false,
        editIndex: null,
        currentPC: null,

        newPC: {},
        newComp: {},
        newGlobalComp: { tipo: '', aec: '', marca: '', serial: '' },
        rams: [],
        discos: [],

        openAddPCModal() {
            this.isEditing = false;
            this.newPC = {
                tipo: 'PC',
                estado_equipo: 'ACTIVO',
                aec: '',
                serial: '',
                marca: '',
                modelo: '',
                sistema_operativo: '',
                procesador: '',
                ip: '',
                observaciones: ''
            };
            this.rams = [{
                capacidad: '8GB',
                tipo: 'DDR4',
                frecuencia: '3200',
                fabricante: ''
            }];
            this.discos = [{
                tipo: 'SSD',
                capacidad: '256GB',
                rpm: '',
                estado: 'NUEVO',
                observaciones: ''
            }];
            this.openAddPC = true;
        },

        editPC(pc, index) {
            // SweetAlert para confirmar antes de entrar a la edición
            Swal.fire({
                title: '¿Editar equipo?',
                text: "Se cargarán los datos para su modificación.",
                icon: 'info',
                showCancelButton: true,
                confirmButtonColor: '#4f46e5',
                cancelButtonColor: '#64748b',
                confirmButtonText: 'Sí, editar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    this.isEditing = true;
                    this.editIndex = index;
                    this.newPC = { ...pc };
                    this.rams = pc.ramData.map(r => ({ ...r }));
                    this.discos = pc.discos.map(d => ({ ...d }));
                    this.openAddPC = true;
                }
            });
        },

        confirmSavePC() {
            // SweetAlert para confirmar el guardado/actualización
            Swal.fire({
                title: this.isEditing ? '¿Actualizar cambios?' : '¿Guardar nuevo equipo?',
                text: "Confirma que los datos ingresados son correctos.",
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#059669',
                cancelButtonColor: '#64748b',
                confirmButtonText: 'Sí, confirmar',
                cancelButtonText: 'Revisar'
            }).then((result) => {
                if (result.isConfirmed) {
                    const data = {
                        ...this.newPC,
                        ramData: [...this.rams],
                        discos: [...this.discos],
                        open: false
                    };

                    if (this.isEditing) {
                        this.pcs[this.editIndex] = {
                            ...data,
                            componentes: this.pcs[this.editIndex].componentes
                        };
                    } else {
                        this.pcs.push({
                            ...data,
                            id: Date.now(),
                            componentes: []
                        });
                    }

                    this.openAddPC = false;

                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: 'El registro se ha procesado correctamente.',
                        timer: 2000,
                        showConfirmButton: false
                    });
                }
            });
        },

        confirmDeletePC(index) {
            Swal.fire({
                title: '¿Eliminar equipo?',
                text: 'Esta acción es irreversible y eliminará todos los datos del equipo.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#e11d48',
                cancelButtonColor: '#64748b',
                confirmButtonText: 'Sí, eliminar permanentemente',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    this.pcs.splice(index, 1);
                    Swal.fire({
                        title: 'Eliminado',
                        text: 'El equipo ha sido removido del sistema.',
                        icon: 'success',
                        timer: 1500,
                        showConfirmButton: false
                    });
                }
            });
        },

        openAddComp(pc) {
            this.currentPC = pc;
            Swal.fire({
                title: 'Vincular Periférico',
                html: `
                    <div class="text-left">
                        <label class="text-[11px] font-bold text-indigo-600 uppercase">Tipo</label>
                        <input id="swal-tipo" class="swal2-input" placeholder="Ej: Mouse">
                        <label class="text-[11px] font-bold text-indigo-600 uppercase">Marca</label>
                        <input id="swal-marca" class="swal2-input" placeholder="Ej: Logitech">
                        <label class="text-[11px] font-bold text-indigo-600 uppercase">Serial</label>
                        <input id="swal-sn" class="swal2-input" placeholder="Ej: SN-9988">
                    </div>
                `,
                showCancelButton: true,
                confirmButtonText: 'Vincular',
                confirmButtonColor: '#4f46e5',
                preConfirm: () => {
                    const tipo = document.getElementById('swal-tipo').value;
                    if (!tipo) return Swal.showValidationMessage('El tipo es obligatorio');
                    return {
                        tipo: tipo,
                        marca: document.getElementById('swal-marca').value,
                        serial: document.getElementById('swal-sn').value
                    }
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    this.currentPC.componentes.push({
                        ...result.value,
                        id: Date.now()
                    });
                }
            });
        },

        confirmDeleteComp(pc, cIdx) {
            Swal.fire({
                title: '¿Quitar componente?',
                text: "¿Deseas desvincular este periférico de este equipo?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#e11d48',
                confirmButtonText: 'Sí, desvincular'
            }).then((result) => {
                if (result.isConfirmed) {
                    pc.componentes.splice(cIdx, 1);
                }
            });
        },

        addGlobalComp() {
            if (!this.newGlobalComp.tipo) return;

            this.componentesGlobales.push({
                ...this.newGlobalComp,
                id: Date.now()
            });

            this.newGlobalComp = { tipo: '', aec: '', marca: '', serial: '' };
            this.openAddComponentGlobal = false;

            Swal.fire({
                icon: 'success',
                title: 'Stock Actualizado',
                timer: 1500,
                showConfirmButton: false
            });
        },

        confirmDeleteGlobal(index) {
            Swal.fire({
                title: '¿Eliminar del stock?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#e11d48',
                confirmButtonText: 'Eliminar'
            }).then((result) => {
                if (result.isConfirmed) {
                    this.componentesGlobales.splice(index, 1);
                }
            });
        }
    }));
});