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
    
    # Extraer mensajes de la sesión si existen
    mensajes_importacion = request.session.pop('mensajes_importacion', None)
    
    return render(request, 'equipo/inventario_equipos.html', {
        'equipos': equipos,
        'lugares': lugares,
        'usuarios': usuarios,
        'mensajes_importacion': mensajes_importacion # Pasar al template
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



User = get_user_model()
# =========================
# IMPORTAR EXCEL
# =========================
import pandas as pd
from django.db import transaction
from django.http import JsonResponse
from .models import Equipo, Ram, Disco, Componente, Lugar


import pandas as pd
import re
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Equipo, Ram, Disco, Componente, Lugar

User = get_user_model()

import pandas as pd
import re
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Equipo, Ram, Disco, Componente, Lugar

User = get_user_model()

def importar_excel_equipos(request):
    if request.method == "POST" and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        
        try:
            # header=1 indica que la cabecera está en la fila 2 del Excel (índice 1)
            # Los datos empezarán automáticamente desde la fila 3
            df = pd.read_excel(archivo, header=1, dtype=str).fillna('')
            
            # Limpiar nombres de columnas por si tienen espacios accidentales
            df.columns = [str(c).strip() for c in df.columns]

            registros_creados = 0
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    # Usamos el nombre exacto que pusiste en tu ejemplo
                    serial_pc = row.get('SERIAL', '').strip()
                    
                    # Si no hay serial, saltamos la fila (puede ser una fila vacía al final)
                    if not serial_pc or serial_pc == '':
                        continue

                    # 1. Buscar Usuario por AEC USUARIO
                    aec_user = row.get('AEC USUARIO', '').strip()
                    usuario_obj = User.objects.filter(username=aec_user).first()
                    
                    # 2. Gestionar Lugar
                    lugar_nombre = row.get('LUGAR', '').split(',')[0].strip()
                    lugar_obj = None
                    if lugar_nombre:
                        lugar_obj, _ = Lugar.objects.get_or_create(nombre=lugar_nombre)

                    # 3. Crear o Actualizar Equipo Principal
                    # IMPORTANTE: update_or_create busca por 'serial'
                    equipo, created = Equipo.objects.update_or_create(
                        serial=serial_pc,
                        defaults={
                            'aec': row.get('AEC EQUIPO', '').strip(),
                            'tipo': row.get('TIPO DE EQUIPO', 'CPU').strip(),
                            'marca': row.get('MARCA', '').strip(),
                            'modelo': row.get('MODELO', '').strip(),
                            'sistema_operativo': row.get('SISTEMA OPERATIVO', '').strip(),
                            'procesador': row.get('PROCESADOR', '').strip(),
                            'ip': row.get('IP USUARIO', '').strip() or None,
                            'estado_equipo': row.get('ESTADO', 'ACTIVO').strip().upper(),
                            'observaciones': row.get('OBSERVACIONES', '').strip(),
                            'id_users': usuario_obj,
                            'id_lugar': lugar_obj,
                        }
                    )

                    # 4. Procesar RAM (Múltiples)
                    txt_ram = row.get('MEMORIA RAM', '')
                    if txt_ram:
                        Ram.objects.filter(equipo=equipo).delete()
                        partes = [p.strip() for p in txt_ram.split(',') if p.strip()]
                        for i in range(0, len(partes), 3):
                            if i < len(partes):
                                frec_str = partes[i+2] if i+2 < len(partes) else ""
                                nums = re.findall(r'\d+', frec_str)
                                frec_int = int(nums[0]) if nums else None
                                
                                Ram.objects.create(
                                    equipo=equipo,
                                    capacidad=partes[i],
                                    tipo=partes[i+1] if i+1 < len(partes) else 'DDR4',
                                    frecuencia=frec_int
                                )

                    # 5. Procesar DISCOS (Múltiples)
                    txt_disco = row.get('DISCO DURO', '')
                    if txt_disco:
                        Disco.objects.filter(equipo=equipo).delete()
                        partes = [p.strip() for p in txt_disco.split(',') if p.strip()]
                        for i in range(0, len(partes), 3):
                            if i < len(partes):
                                Disco.objects.create(
                                    equipo=equipo,
                                    capacidad=partes[i],
                                    tipo=partes[i+1] if i+1 < len(partes) else 'SSD',
                                    estado=partes[i+2] if i+2 < len(partes) else 'ACTIVO'
                                )

                    # 6. Procesar Componentes Periféricos
                    # Buscamos todas las columnas que se llamen "COMPONENTE"
                    idx_componentes = [i for i, col in enumerate(df.columns) if "COMPONENTE" in col.upper()]
                    
                    for start_idx in idx_componentes:
                        tipo_comp = row.iloc[start_idx]
                        if tipo_comp and str(tipo_comp).strip():
                            # Según tu orden: COMPONENTE(0), AEC(1), MARCA(2), MODELO(3), SERIAL(4), ESTADO(5), OBS(6)
                            s_comp = str(row.iloc[start_idx+4]).strip()
                            if s_comp and s_comp != '':
                                Componente.objects.update_or_create(
                                    serial=s_comp,
                                    defaults={
                                        'id_equipo': equipo,
                                        'tipo': tipo_comp,
                                        'aec': row.iloc[start_idx+1],
                                        'marca': row.iloc[start_idx+2],
                                        'modelo': row.iloc[start_idx+3],
                                        'estado': str(row.iloc[start_idx+5]).strip().upper() or 'ACTIVO',
                                        'observaciones': row.iloc[start_idx+6],
                                        'id_users': usuario_obj,
                                        'id_lugar': lugar_obj
                                    }
                                )
                    
                    registros_creados += 1
                    print(f"--> Procesado exitosamente: {serial_pc}")

            return JsonResponse({
                'status': 'success', 
                'message': f'Se procesaron {registros_creados} filas correctamente.'
            })

        except Exception as e:
            print(f"!!! ERROR EN IMPORTACIÓN: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"Error técnico: {str(e)}"}, status=500)

    return JsonResponse({'status': 'error', 'message': 'No se recibió el archivo'}, status=400)















