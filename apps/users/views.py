from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse

from .models import UsersCustomUser, Equipo, Lugar
from .forms import LoginForm, UserCreateForm
from apps.users.decorators import role_required

# Variable auxiliar para mantener el orden consistente en todo el archivo
USER_ORDERING = ('id_lugar__nombre', 'first_name')

# -------------------- AUTENTICACIÓN --------------------
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if user.role == 'admin':
                return redirect('dashboard:admin')
            elif user.role == 'tecnico':
                return redirect('dashboard:tecnico')
            return redirect('dashboard:usuario')
    else:
        form = LoginForm()
    return render(request, 'users/user_login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, '👋 Sesión cerrada correctamente.')
    return redirect('users:login')

# -------------------- PERFIL --------------------
@role_required(roles=["admin","tecnico","usuario"])
def perfil_users(request):
    return render(request, 'users/user_perfil.html')

@role_required(roles=["admin","tecnico","usuario"])
def editar_perfil(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, '✅ Perfil actualizado correctamente.')
        return redirect('users:perfil_users')
    return render(request, 'users/partials/user_editar_perfil.html')

@role_required(roles=["admin","tecnico"])
def cambiar_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '🔒 Contraseña actualizada correctamente.')
            return redirect('users:perfil_users')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/user_cambiar_password.html', {'form': form})

# -------------------- GESTIÓN DE USUARIOS (HTMX) --------------------
@role_required(roles=["admin", "tecnico"])
def user_list(request):
    if request.method == 'POST':
        role = request.POST.get('role', 'usuario').lower()
        codigo = request.POST.get('codigo', '')
        raw_password = (role[:3] + codigo).lower()
        
        try:
            nuevo_usuario = UsersCustomUser.objects.create(
                username=request.POST.get('username'),
                first_name=request.POST.get('nombre', ''),
                last_name=request.POST.get('apellido_p', ''),
                role=role,
                codigo=codigo,
                id_lugar_id=request.POST.get('id_lugar') or None,
                id_equipo_id=request.POST.get('id_equipo') or None,
                email=request.POST.get('email', ''),
                firma=request.FILES.get('firma'),
                is_active=True,
                is_staff=(1 if role == 'admin' else 0),
                password=make_password(raw_password)
            )
            messages.success(request, f"Usuario {nuevo_usuario.username} creado.")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        # Si es HTMX, devolvemos la lista con el ordenamiento estricto
        if request.headers.get('HX-Request'):
            usuarios = UsersCustomUser.objects.all().select_related('id_lugar').order_by(*USER_ORDERING)
            return render(request, 'users/user_list.html', {'usuarios': usuarios})

    # Carga inicial con el ordenamiento estricto
    usuarios = UsersCustomUser.objects.all().select_related('id_lugar', 'id_equipo').order_by(*USER_ORDERING)
    lugares = Lugar.objects.all()
    equipos = Equipo.objects.all()
    
    return render(request, 'users/user_list.html', {
        'usuarios': usuarios,
        'lugares': lugares,
        'equipos': equipos,
    })

@role_required(roles=["admin"])
def eliminar_usuario(request, pk):
    if request.method == "POST":
        usuario = get_object_or_404(UsersCustomUser, pk=pk)
        usuario.delete()
        
        # Al eliminar, refrescamos con el ordenamiento estricto
        if request.headers.get('HX-Request'):
            usuarios = UsersCustomUser.objects.all().select_related('id_lugar').order_by(*USER_ORDERING)
            return render(request, 'users/user_list.html', {'usuarios': usuarios})
            
    return redirect('users:user_list')

@role_required(roles=["admin", "tecnico"])
def editar_usuario_modal(request, pk):
    usuario = get_object_or_404(UsersCustomUser, pk=pk)
    lugares = Lugar.objects.all()
    return render(request, 'users/partials/modal_editar.html', {
        'u': usuario,
        'lugares': lugares
    })