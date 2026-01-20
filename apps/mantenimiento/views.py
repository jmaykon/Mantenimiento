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



def mante_detalle(request):
    return render(request, "mantenimiento/mante_detalle.html")

def mante_cronograma(request):
    return render(request, "mantenimiento/mante_cronograma.html")

@login_required
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
                estado_ticket='pendiente',
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



from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from .models import Ticket
from django.contrib.auth.decorators import login_required


def atender_ticket(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        ticket_id = request.POST.get('id_ticket')
        step = int(request.POST.get('step', 1))

        # Obtener el ticket
        ticket = get_object_or_404(Ticket, id_ticket=ticket_id)

        # Verificar si el ticket ya está completado
        if ticket.estado_ticket == 'completado':
            return JsonResponse({'error': 'Este ticket ya está completado'}, status=400)

        # Asignar técnico si no está asignado
        if ticket.id_tecnico_asignado is None:
            ticket.id_tecnico_asignado = request.user
            ticket.fecha_asignacion = timezone.now()

        # Guardar los campos del ticket si existen
        diagnostico = request.POST.get('diagnostico')
        solucion_aplicada = request.POST.get('solucion_aplicada')
        observaciones_tecnicas = request.POST.get('observaciones_tecnicas')

        if diagnostico is not None:
            ticket.diagnostico = diagnostico
        if solucion_aplicada is not None:
            ticket.solucion_aplicada = solucion_aplicada
        if observaciones_tecnicas is not None:
            ticket.observaciones_tecnicas = observaciones_tecnicas

        # Actualizar el estado según el paso
        if step == 2:
            ticket.estado_ticket = 'en_proceso'
            ticket.fecha_inicio = timezone.now()
        elif step == 3:
            ticket.estado_ticket = 'documentando'
        elif step >= 4:
            ticket.estado_ticket = 'completado'
            ticket.fecha_cierre = timezone.now()
            ticket.modificado_por = request.user

        # Guardar cambios en el ticket
        ticket.save()

        return JsonResponse({
            'estado': ticket.estado_ticket,
            'ultimo_paso': step,
            'id_ticket': ticket.id_ticket
        })

    except Exception as e:
        # Capturar cualquier error y devolverlo
        return JsonResponse({'error': str(e)}, status=500)


# Vista de obtener los datos del ticket
@login_required
def get_ticket_data(request, ticket_id):
    ticket = get_object_or_404(Ticket, id_ticket=ticket_id)
    
    # Mapeo de estado a paso
    estado_a_paso = {
        'pendiente': 1,
        'en_proceso': 2,
        'documentando': 3,
        'completado': 4
    }

    # Obtener el paso actual del ticket basado en su estado
    estado_ticket = ticket.estado_ticket.lower()  # Convertimos a minúsculas para evitar problemas con mayúsculas
    paso_actual = estado_a_paso.get(estado_ticket, 1)  # Si no se encuentra el estado, asignamos el paso 1 por defecto

    # Debugging: Imprime el valor de paso_actual
    print(f"Estado del ticket: {estado_ticket}")
    print(f"Paso actual: {paso_actual}")

    # Devuelve los datos
    return JsonResponse({
        'id_ticket': ticket.id_ticket,
        'descripcion': ticket.descripcion or '',
        'diagnostico': ticket.diagnostico or '',
        'solucion_aplicada': ticket.solucion_aplicada or '',
        'observaciones_tecnicas': ticket.observaciones_tecnicas or '',
        'estado_ticket': ticket.estado_ticket.lower(),  # Asegúrate de que el estado esté en minúsculas
        'paso_actual': paso_actual  # Aquí debería venir el paso correcto
    })

        

from django.db.models import Q

@login_required

def mante_list_pendientes(request):
    tickets = Ticket.objects.filter(estado_ticket='pendiente').order_by('-fecha_creacion')
    return render(request, "mantenimiento/mante_list.html", {'tickets': tickets})



def mante_list_en_proceso(request):
    tickets = Ticket.objects.filter(estado_ticket='en_proceso').order_by('-fecha_creacion')
    return render(request, "mantenimiento/mante_list.html", {'tickets': tickets})


@login_required

def mante_list_documentando(request):
    tickets = Ticket.objects.filter(estado_ticket='documentando').order_by('-fecha_creacion')
    return render(request, "mantenimiento/mante_list.html", {'tickets': tickets})



@login_required
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



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Ticket
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def aprobar_ticket(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        ticket.aprobado = 1  # Marcar como aprobado
        ticket.save()
        return JsonResponse({'success': True, 'ticket_id': ticket.id_ticket})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Ticket

def ticket_datos(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    data = {
        'id_ticket': ticket.id_ticket,
        'diagnostico': ticket.diagnostico or '',
        'solucion_aplicada': ticket.solucion_aplicada or '',
        'observaciones_tecnicas': ticket.observaciones_tecnicas or '',
        'descripcion': ticket.descripcion or '',
        'aprobado': ticket.aprobado,
    }
    return JsonResponse(data)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Ticket

@login_required
def get_ticket_data(request, ticket_id):
    ticket = get_object_or_404(Ticket, id_ticket=ticket_id)

    estado_a_paso = {
        'pendiente': 1,
        'en_proceso': 2,
        'documentando': 3,
        'completado': 4
    }

    return JsonResponse({
        'id_ticket': ticket.id_ticket,
        'descripcion': ticket.descripcion or '',
        'diagnostico': ticket.diagnostico or '',
        'solucion_aplicada': ticket.solucion_aplicada or '',
        'observaciones_tecnicas': ticket.observaciones_tecnicas or '',
        'estado_ticket': ticket.estado_ticket.lower(),
        'paso_actual': estado_a_paso.get(ticket.estado_ticket, 1)
    })







