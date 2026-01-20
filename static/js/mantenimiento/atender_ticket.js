(() => {
    // ==========================
    // ELEMENTOS PRINCIPALES
    // ==========================
    const ticketsContainer = document.getElementById("tickets-container");
    const URL_ATENDER_TICKET = ticketsContainer.dataset.urlAtender;

    const modal = document.getElementById("modal");
    const btnCerrar = modal.querySelector("#btnCerrar");
    const btnCancel = modal.querySelector(".btn-cancel");
    const btnNext = modal.querySelector(".btn-next");

    const steps = modal.querySelectorAll(".step");
    const stepContents = modal.querySelectorAll(".step-content");

    let currentStep = 1; // Valor por defecto (pendiente)
    let currentTicketId = null;

    const btnAtenderList = document.querySelectorAll(".btn-atender");

    // ==========================
    // CSRF
    // ==========================
    function getCSRFToken() {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split("=");
            if (name === "csrftoken") return decodeURIComponent(value);
        }
        return "";
    }

    // ==========================
    // MOSTRAR PASO
    // ==========================
    function showStep(step) {
        steps.forEach((s) => s.classList.remove("step-active", "step-completed"));
        stepContents.forEach((c) => c.classList.add("hidden"));

        steps.forEach((s) => {
            const num = parseInt(s.dataset.step);
            if (num < step) s.classList.add("step-completed");
            else if (num === step) s.classList.add("step-active");
        });

        const content = modal.querySelector(`.step-content[data-step="${step}"]`);
        if (content) content.classList.remove("hidden");

        btnNext.textContent =
            step === 3 ? "Finalizar y Guardar" : "Continuar y Guardar";
    }

    // ==========================
    // OBTENER DATOS DEL TICKET Y ABRIR MODAL
    // ==========================
    async function fetchTicketData(ticketId) {
        try {
            const response = await fetch(`/mantenimiento/get_ticket_data/${ticketId}/`);
            if (!response.ok) throw new Error("Error al obtener datos del ticket");

            const data = await response.json();

            // Verifica si paso_actual está presente
            console.log('Datos del ticket:', data);  // Aquí debería aparecer paso_actual correctamente

            // Guardar ticket actual
            currentTicketId = ticketId;

            // Determinar el paso en base al estado_ticket
            let paso = 1; // Valor por defecto
            if (data.estado_ticket === 'en_proceso') paso = 2;
            else if (data.estado_ticket === 'documentando') paso = 3;
            else if (data.estado_ticket === 'completado') paso = 4;

            // Precargar los datos en el modal
            precargarDatos(data, paso);

            // Mostrar modal
            modal.classList.remove("hidden");
        } catch (error) {
            console.error("Error al obtener el ticket:", error);
            Swal.fire("Error", "No se pudo cargar el ticket", "error");
        }
    }

    function precargarDatos(ticketData, paso) {
        if (!ticketData) return;

        // Asigna el paso correcto
        currentStep = paso || 1;  // Usamos el paso calculado o el valor por defecto (1)

        // Mostrar el paso adecuado en el modal
        showStep(currentStep);

        // Precargar los datos del ticket en el formulario del modal
        const campos = {
            diagnostico: modal.querySelector(".diagnostico"),
            solucion: modal.querySelector(".solucion_aplicada"),
            obs: modal.querySelector(".observaciones_tecnicas"),
            comentario: modal.querySelector(".comentario_usuario")
        };

        // Precargar los datos si existen
        if (campos.diagnostico) campos.diagnostico.value = ticketData.diagnostico || "";
        if (campos.solucion) campos.solucion.value = ticketData.solucion_aplicada || "";
        if (campos.obs) campos.obs.value = ticketData.observaciones_tecnicas || "";
        if (campos.comentario) campos.comentario.value = ticketData.descripcion || "";

        // Habilitar o deshabilitar campos de acuerdo al estado del ticket
        if (ticketData.estado_ticket === "completado") {
            modal.querySelectorAll("textarea").forEach(input => input.disabled = true);
            btnNext.disabled = true;
            btnNext.classList.add("bg-gray-400", "cursor-not-allowed");
        } else {
            modal.querySelectorAll("textarea").forEach(input => input.disabled = false);
            btnNext.disabled = false;
            btnNext.classList.remove("bg-gray-400", "cursor-not-allowed");
        }
    }

    // ==========================
    // CLICK EN BOTÓN ATENDER
    // ==========================
    btnAtenderList.forEach(btn => {
        btn.addEventListener("click", () => {
            const ticketId = btn.dataset.ticketId;
            fetchTicketData(ticketId); // Llamada a la API para obtener los datos del ticket
        });
    });

    // ==========================
    // CERRAR MODAL
    // ==========================
    function cerrarModal() {
        modal.classList.add("hidden");
        currentTicketId = null;
        currentStep = 1;

        // Limpiar todos los inputs del form
        const form = modal.querySelector("#formAtender");
        if (form) form.reset();
    }

    btnCerrar.addEventListener("click", cerrarModal);
    btnCancel.addEventListener("click", cerrarModal);

    // ==========================
    // BOTÓN NEXT
    // ==========================
    btnNext.addEventListener("click", async () => {
        const form = modal.querySelector("#formAtender");
        if (!form || !currentTicketId) return;

        // Confirmación de guardado
        const confirmacion = await Swal.fire({
            title: "¿Guardar cambios?",
            text: "Se guardará el estado actual del ticket",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: "Sí, guardar",
            cancelButtonText: "Cancelar",
            reverseButtons: true
        });

        if (!confirmacion.isConfirmed) return;

        // Calcular siguiente paso
        let nextStep = currentStep < 4 ? currentStep + 1 : 4;

        const formData = new FormData();
        formData.append("id_ticket", currentTicketId);
        formData.append("step", nextStep);

        // Solo si el paso es 3 o más, se guardan los datos del formulario
        if (nextStep >= 3 && form) {
            const diagnostico = form.querySelector(".diagnostico");
            const solucion = form.querySelector(".solucion_aplicada");
            const observaciones = form.querySelector(".observaciones_tecnicas");

            // Verifica si cada campo existe antes de agregar al FormData
            if (diagnostico && diagnostico.value) formData.append("diagnostico", diagnostico.value);
            if (solucion && solucion.value) formData.append("solucion_aplicada", solucion.value);
            if (observaciones && observaciones.value) formData.append("observaciones_tecnicas", observaciones.value);
        }

        try {
            const response = await fetch(URL_ATENDER_TICKET, {
                method: "POST",
                headers: { "X-CSRFToken": getCSRFToken() },
                body: formData,
            });

            if (!response.ok) throw new Error("Error al guardar el ticket");

            const data = await response.json();

            // Confirmación de guardado
            await Swal.fire({
                icon: "success",
                title: "Guardado",
                text: "Los cambios se guardaron correctamente",
                timer: 1200,
                showConfirmButton: false,
            });

            actualizarVistaTicket(data.id_ticket, data.estado);

            currentStep = nextStep;

            // Si ya se completó, cerrar modal
            if (data.estado === "completado") {
                cerrarModal();
            } else {
                showStep(currentStep);
            }

        } catch (error) {
            console.error(error);
            Swal.fire("Error", "No se pudo guardar el ticket", "error");
        }
    });


    // ==========================
    // ACTUALIZAR VISTA DEL TICKET
    // ==========================
    function actualizarVistaTicket(ticketId, estado) {
        const ticket = document.querySelector(`#ticket-${ticketId}`);
        if (!ticket) return;

        const statusSpan = ticket.querySelector(".status span");
        const btnAtender = ticket.querySelector(".btn-atender");

        const estados = {
            pendiente: {
                text: "Pendiente",
                class: "pendiente"
            },
            en_proceso: {
                text: "En Proceso",
                class: "en_proceso"
            },
            documentando: {
                text: "Documentando",
                class: "documentando"
            },
            completado: {
                text: "Completado",
                class: "completado"
            }
        };

        // Cambiar estado visual
        if (statusSpan && estados[estado]) {
            statusSpan.className = estados[estado].class;
            statusSpan.textContent = estados[estado].text;
        }

        // Si está COMPLETADO → bloquear botón
        if (estado === "completado" && btnAtender) {
            btnAtender.textContent = "Completado";
            btnAtender.disabled = true;
            btnAtender.classList.remove("bg-green-500", "hover:bg-green-600");
            btnAtender.classList.add("bg-gray-400", "cursor-not-allowed");
        }
    }
})();
