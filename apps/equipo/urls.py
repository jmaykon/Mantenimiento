from django.urls import path
from . import views

app_name = "equipo"

urlpatterns = [
    path('', views.lista_equipos, name='lista_equipos'),
    path('crear/', views.crear_equipo, name='crear_equipo'),
    path('editar/<int:pk>/', views.editar_equipo, name='editar_equipo'),
    path('eliminar/<int:pk>/', views.eliminar_equipo, name='eliminar_equipo'),

    #compo
    path('componente/crear/', views.crear_componente, name='crear_componente'),
    path('componente/editar/<int:pk>/', views.editar_componente, name='editar_componente'),
    path('componente/eliminar/<int:pk>/', views.eliminar_componente, name='eliminar_componente'),

  
]