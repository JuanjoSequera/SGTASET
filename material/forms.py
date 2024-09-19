from django import forms
from .models import Material

class MaterialForm(forms.ModelForm):

	class Meta: #La clase meta le dice a la clase como comportarse
		model = Material # -> Indica que todo este formulario creado se asociara con una clase ya creada, en este caso la clase Empresa
		fields = ['id_material','codigo_fabricante','nombre_material'] # -> Permite utilizar todos los campos que ya se crearon en la clase Empresa
    
def clean(self):
    cleaned_data = super(MaterialForm, self).clean()
    for field in self.Meta.fields:
        if not cleaned_data.get(field):
            self.add_error(field, "Este campo no puede estar vacío.")