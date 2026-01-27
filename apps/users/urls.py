from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # --- VISTAS DE SESIÓN Y PERFIL ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_users, name='perfil_users'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/password/', views.cambiar_password, name='cambiar_password'),

    # --- GESTIÓN DE USUARIOS ---
    path('gestion/', views.user_list, name='user_list'),
    
    # CAMBIADO: Se agregó '_modal' al name para que coincida con tu error
    path('editar/<int:pk>/', views.editar_usuario_modal, name='editar_usuario_modal'),
    
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
]