from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

# -------------------- DECORADORES DE ROL --------------------
def role_required(roles):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return render(request, 'core/403.html', status=403)
        return _wrapped_view
    return decorator



@login_required
def home_dashboard(request):
    if request.user.role == 'admin':
        template = 'dashboard/admin.html'
    elif request.user.role == 'tecnico':
        template = 'dashboard/tecnico.html'
    else:
        template = 'dashboard/usuario.html'
    return render(request, template)



import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ImportarExcelForm
from apps.lugar.models import Lugar
from apps.equipo.models import Equipo

def importar_excel(request):
    if request.method == 'POST':
        form = ImportarExcelForm(request.POST, request.FILES)

        if form.is_valid():
            archivo = request.FILES['archivo']
            usuario = request.user

            try:
                # --------- LEER EXCEL ---------
                df_equipos = pd.read_excel(archivo, sheet_name='Equipos')
                df_componentes = pd.read_excel(archivo, sheet_name='Componentes')

                equipos_dict = {}

                # --------- IMPORTAR EQUIPOS ---------
                for _, row in df_equipos.iterrows():
                    if Equipo.objects.filter(serial=row['serial']).exists():
                        continue

                    lugar = Lugar.objects.filter(id_lugar=row['id_lugar']).first()

                    equipo = Equipo.objects.create(
                        tipo=row['tipo'],
                        aec=row['aec'],
                        marca=row.get('marca'),
                        modelo=row.get('modelo'),
                        so=row.get('so'),
                        procesador=row.get('procesador'),
                        tipo_ram=row.get('tipo_ram'),
                        ram=row.get('ram'),
                        tipo_disco=row.get('tipo_disco'),
                        disco=row.get('disco'),
                        estado_disco=row.get('estado_disco'),
                        estado_equipo=row.get('estado_equipo', 'ACTIVO'),
                        serial=row['serial'],
                        observaciones=row.get('observaciones'),
                        ip=row.get('ip'),
                        ip_maquina=row.get('ip_maquina'),
                        id_lugar=lugar,
                        id_users=usuario,
                        creado_por=usuario.username
                    )

                    equipos_dict[row['serial']] = equipo

                # --------- IMPORTAR COMPONENTES ---------
                for _, row in df_componentes.iterrows():
                    if Componente.objects.filter(serial=row['serial']).exists():
                        continue

                    equipo = Equipo.objects.filter(serial=row['serial_equipo']).first()
                    if not equipo:
                        continue

                    lugar = Lugar.objects.filter(id_lugar=row['id_lugar']).first()

                    Componente.objects.create(
                        tipo=row['tipo'],
                        aec=row['aec'],
                        marca=row.get('marca'),
                        modelo=row.get('modelo'),
                        serial=row['serial'],
                        estado=row.get('estado', 'Activo'),
                        observaciones=row.get('observaciones'),
                        id_equipo=equipo,
                        id_users=usuario,
                        id_lugar=lugar,
                        creado_por=usuario.username
                    )

                messages.success(request, "Importación realizada correctamente")
                return redirect('importar_excel')

            except Exception as e:
                messages.error(request, f"Error al importar: {e}")

    else:
        form = ImportarExcelForm()

    return render(request, 'importar_excel.html', {'form': form})
