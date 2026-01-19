from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import json
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Ticket, HistorialTicket

from apps.users.decorators import role_required 




@login_required
def mante_list(request):
    tickets = Ticket.objects.order_by('-fecha_creacion')
    return render(request, "mantenimiento/mante_list.html", {'tickets': tickets})



@role_required(roles=["admin", "tecnico","usuario"])
def mante_detalle(request):
    return render(request, "mantenimiento/mante_detalle.html")

@role_required(roles=["admin","usuario"])
def mante_cronograma(request):
    return render(request, "mantenimiento/mante_cronograma.html")

@login_required
@role_required(roles=["admin", "usuario"])
def mante_solicitar(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        colores = request.POST.getlist('colores')
        descripcion = request.POST.get('descripcion')
        prioridad = request.POST.get('prioridad', 'media')

        if tipo == 'recarga_tinta' and not colores:
            return HttpResponse("Por favor, seleccione al menos un color.", status=400)

        try:
            if tipo == 'recarga_tinta':
                detalle = "Todos los colores" if "todos" in colores else ", ".join(colores).title()
            elif tipo == 'tonner':
                detalle = "Recarga de Tonner"
            elif tipo == 'soporte_usuario':
                detalle = "Soporte Técnico Directo"
            else:
                detalle = "Mantenimiento General"

            nuevo_ticket = Ticket.objects.create(
                id_users=request.user,
                tipo_soporte=tipo,
                insumos_utilizados=detalle,
                descripcion=descripcion,
                estado_ticket='Pendiente',
                prioridad=prioridad,
                creado_por=request.user.username
            )

            response = HttpResponse("") 
            response['HX-Trigger'] = json.dumps({
                "eventoTicketCreado": {"numero": nuevo_ticket.id_ticket}
            })
            return response

        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'mantenimiento/mante_solicitar.html')



@login_required
def atender_ticket(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    ticket_id = request.POST.get('id_ticket')
    step = int(request.POST.get('step', 1))

    ticket = get_object_or_404(Ticket, id_ticket=ticket_id)

    if ticket.estado_ticket == 'completado':
        return JsonResponse({'error': 'Este ticket ya está completado'}, status=400)

    # Asignar técnico si no existe
    if ticket.id_tecnico_asignado is None:
        ticket.id_tecnico_asignado = request.user
        ticket.fecha_asignacion = timezone.now()

    # Guardar los campos de documentando si existen
    diagnostico = request.POST.get('diagnostico')
    solucion_aplicada = request.POST.get('solucion_aplicada')
    observaciones_tecnicas = request.POST.get('observaciones_tecnicas')

    if diagnostico is not None:
        ticket.diagnostico = diagnostico
    if solucion_aplicada is not None:
        ticket.solucion_aplicada = solucion_aplicada
    if observaciones_tecnicas is not None:
        ticket.observaciones_tecnicas = observaciones_tecnicas

    # Actualizar estado según el paso
    if step == 2:
        ticket.estado_ticket = 'en_proceso'
        ticket.fecha_inicio = timezone.now()
    elif step == 3:
        ticket.estado_ticket = 'documentando'
    elif step >= 4:
        ticket.estado_ticket = 'completado'
        ticket.fecha_cierre = timezone.now()
        ticket.modificado_por = request.user

    ticket.save() 

    return JsonResponse({
        'estado': ticket.estado_ticket,
        'ultimo_paso': step,
        'id_ticket': ticket.id_ticket
    })

@login_required
def get_ticket_data(request, ticket_id):
    ticket = get_object_or_404(Ticket, id_ticket=ticket_id)

    # Mapear estado a paso
    estado_a_paso = {
        'pendiente': 1,
        'en_proceso': 2,
        'documentando': 3,
        'completado': 4,
        'cancelado': 0
    }

    # Manejar usuario nulo
    usuario = ""
    if ticket.id_users:
        usuario = f"{ticket.id_users.nombre} {ticket.id_users.apellido_p} {ticket.id_users.apellido_m}"

    return JsonResponse({
        'id_ticket': ticket.id_ticket,
        'descripcion': ticket.descripcion or '',
        'diagnostico': ticket.diagnostico or '',
        'solucion': ticket.solucion_aplicada or '',
        'observaciones': ticket.observaciones_tecnicas or '',
        'estado_ticket': ticket.estado_ticket,
        'paso_actual': estado_a_paso.get(ticket.estado_ticket, 1),
        'usuario': usuario
    })


from django.db.models import Q

@login_required
@role_required(roles=["admin", "tecnico", "usuario"])
def mante_list_pendientes(request):
    user = request.user
    if user.is_superuser or 'usuario' in [role.name for role in user.roles.all()]:
        # Admin y usuario pueden ver todos los tickets pendientes
        tickets = Ticket.objects.filter(estado_ticket='pendiente').order_by('-fecha_creacion')
    else:
        # Los técnicos solo ven los pendientes asignados a ellos o no asignados
        tickets = Ticket.objects.filter(
            estado_ticket='pendiente',
        ).filter(
            Q(id_tecnico_asignado__isnull=True) | Q(id_tecnico_asignado=user)
        ).order_by('-fecha_creacion')

    return render(request, "mantenimiento/mante_list.html", {'tickets': tickets})

@login_required
@role_required(roles=["admin", "tecnico", "usuario"])
def mante_list_en_proceso(request):
    user = request.user
    if user.is_superuser or 'usuario' in [role.name for role in user.roles.all()]:
        # Admin y usuario ven todos los tickets en proceso
        tickets = Ticket.objects.filter(estado_ticket='en_proceso').order_by('-fecha_creacion')
    else:
        # Los técnicos solo ven los tickets asignados a ellos en "en_proceso"
        tickets = Ticket.objects.filter(
            estado_ticket='en_proceso',
            id_tecnico_asignado=user
        ).order_by('-fecha_creacion')

    return render(request, "mantenimiento/mante_list.html", {'tickets': tickets})

@login_required
@role_required(roles=["admin", "tecnico", "usuario"])
def mante_list_documentando(request):
    user = request.user
    if user.is_superuser or 'usuario' in [role.name for role in user.roles.all()]:
        # Admin y usuario ven todos los tickets documentando
        tickets = Ticket.objects.filter(estado_ticket='documentando').order_by('-fecha_creacion')
    else:
        # Los técnicos solo ven los tickets asignados a ellos en "documentando"
        tickets = Ticket.objects.filter(
            estado_ticket='documentando',
            id_tecnico_asignado=user
        ).order_by('-fecha_creacion')

    return render(request, "mantenimiento/mante_list.html", {'tickets': tickets})


@login_required
@role_required(roles=["admin", "tecnico","usuario"])
def mante_list_completado(request):
    tickets = Ticket.objects.filter(estado_ticket='completado').order_by('-fecha_creacion')
    return render(request, "mantenimiento/mante_list.html", {'tickets': tickets})



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Ticket, ReporteMantenimiento

@login_required
def generar_reporte(request, id_ticket):
    ticket = get_object_or_404(Ticket, id_ticket=id_ticket)

    # Evitar duplicados
    reporte, creado = ReporteMantenimiento.objects.get_or_create(
        id_ticket=ticket,
        defaults={
            'id_equipo': ticket.id_equipo,
            'id_lugar': ticket.id_lugar,
            'descripcion': ticket.descripcion,
            'creado_por': request.user.username,
            'id_elaborado_por': request.user,
        }
    )

    # Redirige al detalle o edición del reporte
    return redirect('mantenimiento:detalle_reporte', reporte.id_reporte)


