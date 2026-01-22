from django import forms
from .models import Equipo
from .models import Componente

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        exclude = ('fecha_eliminacion',)





# forms.py
from django import forms
from .models import Componente


class ComponenteForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = [
            'tipo', 'aec', 'marca_ref', 'modelo', 'serial',
            'id_equipo', 'id_lugar', 'estado', 'observaciones'
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-input'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
        }