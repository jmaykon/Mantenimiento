from .models import Equipo
from .models import Lugar
from .models import Componente
from .forms import EquipoForm
from django.utils import timezone
from apps.users.decorators import role_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from apps.users.models import UsersCustomUser
from .models import Equipo, Componente
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Equipo
from .forms import EquipoForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Equipo
from .forms import EquipoForm
@role_required(roles=["admin", "tecnico"])
def lista_equipos(request):
    equipos = Equipo.objects.select_related(
        'id_lugar', 'id_users'
    ).filter(fecha_eliminacion__isnull=True)

    monitores = Componente.objects.filter(
        tipo__iexact="Monitor",
        fecha_eliminacion__isnull=True
    )

    impresoras = Componente.objects.filter(
        tipo__iexact="Impresora",
        fecha_eliminacion__isnull=True
    )

    return render(request, 'equipo/partials/equipo_table.html', {
        'equipos': equipos,
        'monitores': monitores,
        'impresoras': impresoras
    })

def crear_equipo(request):
    if request.method == "POST":
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            equipos = Equipo.objects.filter(fecha_eliminacion__isnull=True)
            return render(request, 'equipo/partials/equipo_table.html', {
                'equipos': equipos
            })
    else:
        form = EquipoForm()

    return render(request, 'equipo/partials/equipo_form.html', {
        'form': form
    })

def editar_equipo(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk, fecha_eliminacion__isnull=True)

    if request.method == "POST":
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            return render(request, 'equipo/partials/equipo_table.html', {
                'equipos': Equipo.objects.filter(fecha_eliminacion__isnull=True)
            })
    else:
        form = EquipoForm(instance=equipo)

    return render(request, 'equipo/partials/equipo_form.html', {
        'form': form,
        'accion': 'Editar',
        'equipo': equipo
    })

def eliminar_equipo(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)

    equipo.fecha_eliminacion = timezone.now()
    equipo.save()

    return render(request, 'equipo/partials/equipo_table.html', {
        'equipos': Equipo.objects.filter(fecha_eliminacion__isnull=True)
    })

   
# COMPON
from .forms import ComponenteForm
from django.utils import timezone

from django.shortcuts import render, redirect
from .forms import ComponenteForm

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import ComponenteForm
from .models import Componente

from django.shortcuts import render, redirect
from .forms import ComponenteForm
from .models import Componente

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Componente, Equipo
from .forms import ComponenteForm

@login_required
def crear_componente(request):
    if request.method == 'POST':
        form = ComponenteForm(request.POST)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.id_users = request.user
            comp.save()
            return JsonResponse({'success': True})
    else:
        form = ComponenteForm()
    return render(request, 'mantenimiento/componente_form.html', {'form': form})


@login_required
def editar_componente(request, pk):
    comp = get_object_or_404(Componente, pk=pk)
    if request.method == 'POST':
        form = ComponenteForm(request.POST, instance=comp)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
    else:
        form = ComponenteForm(instance=comp)
    return render(request, 'mantenimiento/componente_form.html', {'form': form})


@login_required

def eliminar_componente(request, pk):
    comp = get_object_or_404(Componente, pk=pk)
    comp.soft_delete(usuario=request.user.username)
    return JsonResponse({'success': True})
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   