from django.urls import path
from . import views

app_name = "equipo"

urlpatterns = [
    path('', views.lista_equipos, name='lista_equipos'),
    path('guardar/', views.guardar_equipo, name='guardar_equipo'),
    path('editar/<int:id_equipo>/', views.editar_equipo, name='editar_equipo'),
    path('eliminar/<int:id_equipo>/', views.eliminar_equipo, name='eliminar_equipo'),
    path('importar-excel/', views.importar_excel_equipos, name='importar_excel_equipos'),
    
]
    



