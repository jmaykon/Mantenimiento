from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Equipo, Lugar, Ram, Disco

User = get_user_model()

def lista_equipos(request):
    """Vista principal para listar equipos"""
    equipos = Equipo.objects.all().prefetch_related('rams', 'discos')
    lugares = Lugar.objects.all()
    usuarios = User.objects.all()
    
    return render(request, 'equipo/inventario_equipos.html', {
        'equipos': equipos,
        'lugares': lugares,
        'usuarios': usuarios
    })

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # Solo si tienes problemas con el token

@transaction.atomic # Para que si algo falla, no se guarde nada a medias
def guardar_equipo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # 1. Crear el Equipo
            # Nota: Asegúrate de que los nombres de los campos coincidan con tu modelo
            nuevo_equipo = Equipo.objects.create(
                tipo=data.get('tipo'),
                aec=data.get('aec'),
                sistema_operativo=data.get('so'),
                ip=data.get('ip'),
                marca=data.get('marca'),
                modelo=data.get('modelo'),
                procesador=data.get('procesador'),
                serial=data.get('serial'),
                estado_equipo=data.get('estado'),
                id_lugar_id=data.get('lugar_id') if data.get('lugar_id') else None,
                id_users_id=data.get('user_id') if data.get('user_id') else None,
                observaciones=data.get('observaciones')
            )

            # 2. Guardar RAMs dinámicas
            rams_data = data.get('rams', [])
            for r in rams_data:
                if r.get('capacidad'): # Evitar guardar filas vacías
                    Ram.objects.create(
                        id_equipo=nuevo_equipo,
                        capacidad=r.get('capacidad'),
                        tipo=r.get('tipo'),
                        frecuencia=r.get('frecuencia')
                    )

            # 3. Guardar Discos dinámicos
            discos_data = data.get('discos', [])
            for d in discos_data:
                if d.get('capacidad'):
                    Disco.objects.create(
                        id_equipo=nuevo_equipo,
                        capacidad=d.get('capacidad'),
                        tipo=d.get('tipo')
                    )

            return JsonResponse({
                'status': 'success', 
                'message': f'Equipo {nuevo_equipo.serial} guardado con éxito'
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def editar_equipo(request, id_equipo):
    equipo = get_object_or_404(Equipo, id_equipo=id_equipo)
    
    if request.method == 'POST':
        # 1. Actualizar campos básicos
        equipo.ip = request.POST.get('ip')
        equipo.sistema_operativo = request.POST.get('sistema_operativo')
        equipo.estado_equipo = request.POST.get('estado_equipo')
        equipo.marca = request.POST.get('marca')
        equipo.modelo = request.POST.get('modelo')
        equipo.procesador = request.POST.get('procesador')
        equipo.id_lugar_id = request.POST.get('id_lugar')
        equipo.id_users_id = request.POST.get('id_users') or None
        equipo.save()

        # 2. Actualizar RAMs (Borramos las anteriores y creamos nuevas)
        equipo.rams.all().delete()
        caps_ram = request.POST.getlist('ram_capacidad[]')
        tipos_ram = request.POST.getlist('ram_tipo[]')
        for cap, tipo in zip(caps_ram, tipos_ram):
            if cap: # Solo si tiene capacidad escrita
                Ram.objects.create(id_equipo=equipo, capacidad=cap, tipo=tipo)

        # 3. Actualizar Discos
        equipo.discos.all().delete()
        caps_disco = request.POST.getlist('disco_capacidad[]')
        tipos_disco = request.POST.getlist('disco_tipo[]')
        for cap, tipo in zip(caps_disco, tipos_disco):
            if cap:
                Disco.objects.create(id_equipo=equipo, capacidad=cap, tipo=tipo)

        # 4. Respuesta HTMX
        # Retornamos solo el partial de la lista para que hx-target="#lista-equipos" lo actualice
        equipos = Equipo.objects.all().order_by('-id_equipo')
        response = render(request, 'equipo/partials/list_equipos_partial.html', {'equipos': equipos})
        
        # ESTA ES LA MAGIA: Le dice a Alpine que cierre el modal
        response['HX-Trigger'] = 'cerrar-modal-editar'
        return response

    # Si es GET, mostramos el modal con los datos
    context = {
        'equipo': equipo,
        'lugares': Lugar.objects.all(),
        'usuarios': User.objects.all(),
    }
    return render(request, 'equipo/partials/editar.html', context)







def eliminar_equipo(request, id_equipo):
    """Vista para eliminar un equipo optimizada para HTMX"""
    if request.method in ["POST", "DELETE"]:
        equipo = get_object_or_404(Equipo, id_equipo=id_equipo)
        equipo.delete()
        
        # Si la petición viene de HTMX, respondemos con un cuerpo vacío 
        # para que 'closest .card-equipo' se elimine del DOM.
        if request.headers.get('HX-Request'):
            return HttpResponse("") 
            
        # Si no es HTMX (fallback), redirigimos
        return redirect('equipo:lista_equipos')
    
    return HttpResponse("Método no permitido", status=405)