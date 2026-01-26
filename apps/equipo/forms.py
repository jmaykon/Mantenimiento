from django import forms
from django.conf import settings
from django.apps import apps  # Importar apps para obtener el modelo de usuario dinámicamente
from .models import Equipo
from apps.lugar.models import Lugar
# In apps/equipo/forms.py
from django.contrib.auth import get_user_model
# In apps/equipo/views.py
from .models import Equipo
# Obtener el modelo de usuario dinámicamente
User = apps.get_model(settings.AUTH_USER_MODEL)

class EquipoForm(forms.ModelForm):
    ESTADOS = [
        ("ACTIVO", "Activo"),
        ("MANTENIMIENTO", "Mantenimiento"),
        ("INACTIVO", "Inactivo"),
    ]

    tipo = forms.CharField(max_length=50)
    aec = forms.CharField(max_length=50)
    marca = forms.CharField(max_length=50, required=False)
    modelo = forms.CharField(max_length=50, required=False)
    sistema_operativo = forms.CharField(max_length=50, required=False)
    procesador = forms.CharField(max_length=50, required=False)
    estado_equipo = forms.ChoiceField(choices=ESTADOS, initial="ACTIVO")
    serial = forms.CharField(max_length=50)
    observaciones = forms.CharField(max_length=300, required=False, widget=forms.Textarea)
    ip = forms.GenericIPAddressField(required=False)
    id_lugar = forms.ModelChoiceField(queryset=Lugar.objects.all(), required=False)
    id_users = forms.ModelChoiceField(queryset=User.objects.all(), required=False)  # Usar el modelo de usuario dinámicamente

    class Meta:
        model = Equipo
        fields = [
                    'tipo', 'aec', 'marca', 'modelo', 'sistema_operativo', 
                    'procesador', 'estado_equipo', 'serial', 'ip', 
                    'id_lugar', 'id_users', 'observaciones'
                ]
    def clean_serial(self):
        serial = self.cleaned_data.get('serial')
        if Equipo.objects.filter(serial=serial).exists():
            raise forms.ValidationError('Ya existe un equipo con este serial.')
        return serial
