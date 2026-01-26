from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Equipo, Lugar, Ram, Disco

User = get_user_model()


# =========================
# LISTA DE EQUIPOS
# =========================
def lista_equipos(request):
    equipos = Equipo.objects.all().prefetch_related('rams', 'discos')
    lugares = Lugar.objects.all()
    usuarios = User.objects.all()
    
    return render(request, 'equipo/inventario_equipos.html', {
        'equipos': equipos,
        'lugares': lugares,
        'usuarios': usuarios
    })


# =========================
# GUARDAR EQUIPO
# =========================
@transaction.atomic
def guardar_equipo(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        import json
        data = json.loads(request.body)
        serial = data.get('serial')
        ip = data.get('ip')

        # Validaciones
        if Equipo.objects.filter(serial=serial).exists():
            return JsonResponse({'status': 'error', 'message': f'El serial {serial} ya está registrado'}, status=400)

        if ip and Equipo.objects.filter(ip=ip).exists():
            return JsonResponse({'status': 'error', 'message': f'La IP {ip} ya está asignada a otro equipo'}, status=400)

        # Crear equipo
        equipo = Equipo.objects.create(
            tipo=data.get('tipo'),
            aec=data.get('aec'),
            sistema_operativo=data.get('so'),
            ip=ip,
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            procesador=data.get('procesador'),
            serial=serial,
            estado_equipo=data.get('estado'),
            id_lugar_id=data.get('lugar_id') or None,
            id_users_id=data.get('user_id') or None,
            observaciones=data.get('observaciones')
        )

        # RAMs dinámicas
        for r in data.get('rams', []):
            if r.get('capacidad'):
                Ram.objects.create(
                    equipo=equipo,
                    capacidad=r.get('capacidad'),
                    tipo=r.get('tipo'),
                    frecuencia=r.get('frecuencia') or None
                )

        # Discos dinámicos
        for d in data.get('discos', []):
            if d.get('capacidad'):
                Disco.objects.create(
                    equipo=equipo,
                    capacidad=d.get('capacidad'),
                    tipo=d.get('tipo')
                )

        return JsonResponse({'status': 'success', 'message': f'Equipo {serial} guardado con éxito'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# =========================
# EDITAR EQUIPO
# =========================
@transaction.atomic
def editar_equipo(request, id_equipo):
    try:
        equipo = get_object_or_404(Equipo, id_equipo=id_equipo)

        if request.method == 'POST':
            ip = request.POST.get('ip')
            if ip and Equipo.objects.filter(ip=ip).exclude(id_equipo=id_equipo).exists():
                return JsonResponse({'status': 'error', 'message': f'La IP {ip} ya está asignada a otro equipo'}, status=400)

            # Actualizar campos básicos
            equipo.tipo = request.POST.get('tipo')
            equipo.aec = request.POST.get('aec')
            equipo.ip = ip
            equipo.sistema_operativo = request.POST.get('sistema_operativo')
            equipo.estado_equipo = request.POST.get('estado_equipo')
            equipo.marca = request.POST.get('marca')
            equipo.modelo = request.POST.get('modelo')
            equipo.procesador = request.POST.get('procesador')
            equipo.id_lugar_id = request.POST.get('id_lugar') or None
            equipo.id_users_id = request.POST.get('id_users') or None
            equipo.observaciones = request.POST.get('observaciones')
            equipo.save()

            # Actualizar RAMs
            equipo.rams.all().delete()
            for cap, tipo, freq in zip(request.POST.getlist('ram_capacidad[]'),
                                       request.POST.getlist('ram_tipo[]'),
                                       request.POST.getlist('ram_frecuencia[]')):
                if cap:
                    Ram.objects.create(equipo=equipo, capacidad=cap, tipo=tipo, frecuencia=freq or None)

            # Actualizar Discos
            equipo.discos.all().delete()
            for cap, tipo in zip(request.POST.getlist('disco_capacidad[]'),
                                  request.POST.getlist('disco_tipo[]')):
                if cap:
                    Disco.objects.create(equipo=equipo, capacidad=cap, tipo=tipo)

            # Responder HTMX
            equipos = Equipo.objects.all().order_by('-id_equipo')
            response = render(request, 'equipo/partials/lista_equipos_cards.html', {'equipos': equipos})
            response['HX-Trigger'] = 'cerrar-modal-editar'
            return response

        # GET -> mostrar modal
        context = {
            'equipo': equipo,
            'lugares': Lugar.objects.all(),
            'usuarios': User.objects.all(),
        }
        return render(request, 'equipo/partials/editar.html', context)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# =========================
# ELIMINAR EQUIPO
# =========================
@transaction.atomic
def eliminar_equipo(request, id_equipo):
    try:
        if request.method not in ["POST", "DELETE"]:
            return HttpResponse("Método no permitido", status=405)

        equipo = get_object_or_404(Equipo, id_equipo=id_equipo)
        equipo.delete()

        if request.headers.get('HX-Request'):
            return HttpResponse("")  # HTMX elimina el card automáticamente
        return redirect('equipo:lista_equipos')

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



# apps/equipo/views.py
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
from apps.equipo.models import Equipo, Ram, Disco
from apps.lugar.models import Lugar
from django.contrib.auth import get_user_model

User = get_user_model()
# =========================
# IMPORTAR EXCEL
# =========================
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Equipo, Ram, Disco
from apps.lugar.models import Lugar
from django.contrib.auth import get_user_model

User = get_user_model()

import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Equipo, Ram, Disco
from apps.lugar.models import Lugar
from django.contrib.auth import get_user_model

User = get_user_model()

