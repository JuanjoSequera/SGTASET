from django import forms
from .models import Transferencias

class TransferenciaForm(forms.ModelForm):
    class Meta:
        model = Transferencias
        fields = ['ID_MXD_Origen', 'ID_MXD_Destino', 'ID_Empleado', 'Cantidad']
