function componenteDashboard() {
    return {
        componentesGlobales: [],
        newComp: {},
        openAddComponentGlobal: false,

        // AGREGAR COMPONENTE GLOBAL
        addComponenteGlobal() {
            if (!this.newComp.tipo) return;

            this.componentesGlobales.push({
                id: Date.now(),
                tipo: this.newComp.tipo,
                aec: this.newComp.aec || 'AEC-' + Math.floor(Math.random() * 9000)
            });

            this.newComp = {};
            this.openAddComponentGlobal = false;
        }
    }
}
