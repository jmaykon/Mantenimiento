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

  let currentStep = 1;
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
  // PRECARGAR DATOS DEL TICKET
  // ==========================

  function precargarDatos(ticketData) {
    if (!ticketData) return;

    currentStep = ticketData.paso_actual || 1;
    showStep(currentStep);

    const campos = {
      diagnostico: modal.querySelector(".diagnostico"),
      solucion: modal.querySelector(".solucion_aplicada"),
      obs: modal.querySelector(".observaciones_tecnicas"),
      comentario: modal.querySelector(".comentario_usuario")
    };

    if (campos.diagnostico) campos.diagnostico.value = ticketData.diagnostico || "";
    if (campos.solucion) campos.solucion.value = ticketData.solucion || "";
    if (campos.obs) campos.obs.value = ticketData.observaciones || "";
    if (campos.comentario) campos.comentario.value = ticketData.descripcion || "";
  }



  // ==========================
  // OBTENER DATOS DEL TICKET
  // ==========================
  async function fetchTicketData(ticketId) {
    try {
      const response = await fetch(
        `/mantenimiento/get_ticket_data/${ticketId}/`
      );
      if (!response.ok) throw new Error("Error al obtener datos del ticket");

      const data = await response.json();

      // Guardar ticket actual
      currentTicketId = ticketId;

      // Precargar datos en el modal de forma segura
      precargarDatos(data);

      // Mostrar el modal
      modal.classList.remove("hidden");
    } catch (error) {
      console.error("Error al obtener el ticket:", error);
      Swal.fire("Error", "No se pudo cargar el ticket", "error");
    }
  }

  // ==========================
  // CLICK ATENDER
  // ==========================
  btnAtenderList.forEach((btn) => {
    btn.addEventListener("click", () => {
      const ticketId = btn.dataset.ticketId;
      fetchTicketData(ticketId);
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

    // 🔔 SWEET ALERT DE CONFIRMACIÓN
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

    // 👉 calcular siguiente paso
    let nextStep = currentStep < 4 ? currentStep + 1 : 4;

    const formData = new FormData();
    formData.append("id_ticket", currentTicketId);
    formData.append("step", nextStep);

    if (nextStep >= 3) {
      formData.append("diagnostico", form.querySelector(".diagnostico")?.value || "");
      formData.append("solucion_aplicada", form.querySelector(".solucion_aplicada")?.value || "");
      formData.append("observaciones_tecnicas", form.querySelector(".observaciones_tecnicas")?.value || "");
    }

    try {
      const response = await fetch(URL_ATENDER_TICKET, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },
        body: formData,
      });

      if (!response.ok) throw new Error("Error al guardar el ticket");

      const data = await response.json();

      // ✅ CONFIRMACIÓN DE GUARDADO
      await Swal.fire({
        icon: "success",
        title: "Guardado",
        text: "Los cambios se guardaron correctamente",
        timer: 1200,
        showConfirmButton: false,
      });

      actualizarVistaTicket(data.id_ticket, data.estado);

      currentStep = nextStep;

      if (currentStep < 4) {
        showStep(currentStep);
      } else {
        cerrarModal();
      }

    } catch (error) {
      console.error(error);
      Swal.fire("Error", "No se pudo guardar el ticket", "error");
    }
  });


  function actualizarVistaTicket(ticketId, estado) {
    const ticket = document.querySelector(`#ticket-${ticketId}`);
    if (!ticket) return;

    // actualizar atributo
    ticket.dataset.estado = estado;

    // estado visual
    const statusSpan = ticket.querySelector(".status span");

    const estados = {
      pendiente: { text: "Pendiente", class: "pendiente" },
      en_proceso: { text: "En Proceso", class: "en_proceso" },
      documentando: { text: "Documentando", class: "documentando" },
      completado: { text: "Completado", class: "completado" }
    };

    if (statusSpan && estados[estado]) {
      statusSpan.className = estados[estado].class;
      statusSpan.textContent = estados[estado].text;
    }

    // botón atender
    const btnAtender = ticket.querySelector(".btn-atender");

    if (estado === "completado") {
      btnAtender.textContent = "Completado";
      btnAtender.disabled = true;
      btnAtender.classList.remove("bg-green-500", "hover:bg-green-600");
      btnAtender.classList.add("bg-gray-400", "cursor-not-allowed");
    }
  }





})();
