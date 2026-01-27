from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Lugar
from .forms import LugarForm
from apps.users.decorators import role_required
from django.http import HttpResponse

@role_required(roles=["admin", "tecnico"])
def lista_lugares(request):
    lugares = Lugar.objects.all().order_by('nombre', 'area')
    form = LugarForm()
    return render(request, 'lugar/lugar_list.html', {
        'lugares': lugares,
        'form': form
    })


# views.py
from django.shortcuts import render
from .models import Lugar

from django.shortcuts import render
from .models import Lugar  # Asegúrate de importar tu modelo
from django.views.decorators.http import require_POST

@require_POST
def agregar_lugares(request):
    # 1. Extraer datos del formulario
    nombre = request.POST.get('nombre')
    ciudad = request.POST.get('ciudad')
    direccion = request.POST.get('direccion')
    area = request.POST.get('area')

    # 2. Crear el nuevo registro
    Lugar.objects.create(
        nombre=nombre,
        ciudad=ciudad,
        direccion=direccion,
        area=area
    )

    # 3. Recuperar TODOS los lugares ORDENADOS por nombre
    # ¡ESTO ES CLAVE! Sin el order_by, el regroup de Django 
    # creará bloques duplicados si no son adyacentes.
    lugares = Lugar.objects.all().order_by('nombre', 'area')

    # 4. Retornar solo el fragmento que HTMX necesita
    # Si usas el mismo template, asegúrate de pasar 'lugares'
    return render(request, 'lugar/lugar_list.html', {'lugares': lugares})


@role_required(roles=["admin", "tecnico"])
def editar_lugar(request, id):
    lugar = get_object_or_404(Lugar, id_lugar=id)

    if request.method == "GET" and request.headers.get("HX-Request"):
        form = LugarForm(instance=lugar)
        return render(request, "lugar/partials/lugar_edit_form.html", {"form": form, "lugar": lugar})

    if request.method == "POST" and request.headers.get("HX-Request"):
        form = LugarForm(request.POST, instance=lugar)
        if form.is_valid():
            lugar = form.save(commit=False)
            lugar.modificado_por = request.user.username
            lugar.save()

            response = render(
                request,
                "lugar/partials/lugar_table.html",
                {"lugares": Lugar.objects.order_by('nombre', 'area')}
            )
            response["HX-Trigger"] = f'{{"lugarEditado":"{lugar.nombre}"}}'
            return response



@role_required(roles=["admin", "tecnico"])
def eliminar_lugar(request, id):
    if request.headers.get("HX-Request"):
        lugar = get_object_or_404(Lugar, id_lugar=id)
        lugar.save()

        lugar.delete()  
        return render(
            request,
            "lugar/partials/lugar_table.html",
            {"lugares": Lugar.objects.all().order_by('nombre', 'area')}
        )

# ------------------------------
# Subir Excel y procesar lugares
# ------------------------------
from django.views.decorators.csrf import csrf_exempt
import openpyxl
import openpyxl
from django.shortcuts import redirect
from .models import Lugar

from django.http import HttpResponse

from django.http import HttpResponse

from django.http import HttpResponse


def subir_excel(request):
    if request.method != "POST":
        return redirect("lugar:lista_lugares")

    archivo = request.FILES.get("archivo")
    if not archivo:
        return redirect("lugar:lista_lugares")

    wb = openpyxl.load_workbook(archivo)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, min_col=1, max_col=4, values_only=True):
        nombre, direccion, area, ciudad = row
        if not nombre:
            continue
        Lugar.objects.create(
            nombre=nombre.strip().upper(),  # 👈 AQUÍ
            direccion=direccion,
            area=area,
            ciudad=ciudad,
            creado_por=request.user.username
        )


    response = HttpResponse(status=204)
    # Esto disparará un trigger en JS para cerrar modal y mostrar alerta
    response["HX-Trigger"] = '{"excelSubido":"Excel importado correctamente"}'
    return response












