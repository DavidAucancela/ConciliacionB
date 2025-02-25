from django import forms
from .models import Cuenta, TransaccionContables

class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['saldo', 'moneda']

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = TransaccionContables
        # Incluye solo los campos existentes, por ejemplo:
        fields = ['monto', 'tipo']

#class UploadFileForm(forms.Form):
#    archivo_bancario = forms.FileField(label='Archivo de movimientos bancarios')
#    archivo_empresarial = forms.FileField(label='Archivo de movimientos empresariales')

class UploadFileForm(forms.Form):
    csv_file = forms.FileField()