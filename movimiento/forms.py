from django import forms
from .models import Movimiento

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['ID_MXD', 'ID_Empleado', 'Concepto', 'Cantidad', 'Fecha', 'Signo']
