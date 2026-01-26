from django.urls import path
from . import views

app_name = "mantenimiento"

urlpatterns = [
    path("lista/", views.mante_list, name="mante_list"),
    path("detalle/", views.mante_detalle, name="mante_detalle"),
    path("cronograma/", views.mante_cronograma, name="mante_cronograma"),
    path("solicitar/", views.mante_solicitar, name="mante_solicitar"),
    path('atender_ticket/', views.atender_ticket, name='atender_ticket'),
    path("get_ticket_data/<int:ticket_id>/", views.get_ticket_data, name="get_ticket_data"),
    path("lista/pendientes", views.mante_list_pendientes, name="mante_list_pendientes"),
    path("lista/en_proceso", views.mante_list_en_proceso, name="mante_list_en_proceso"),
    path("lista/documentando", views.mante_list_documentando, name="mante_list_documentando"),
    path("lista/completado", views.mante_list_completado, name="mante_list_completado"),
    # Aquí añades la ruta para aprobar ticket
    path('aprobar-ticket/<int:ticket_id>/', views.aprobar_ticket, name='aprobar_ticket'),
    # urls.py
    path('ticket-datos/<int:ticket_id>/', views.get_ticket_data, name='ticket-datos'),
]
