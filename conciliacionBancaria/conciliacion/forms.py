from django import forms
from .models import Cuenta, Transaccion

class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['saldo', 'moneda']

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['cuenta_origen', 'cuenta_destino', 'monto', 'tipo']

class UploadFileForm(forms.Form):
    archivo_bancario = forms.FileField(label='Archivo de movimientos bancarios')
    archivo_empresarial = forms.FileField(label='Archivo de movimientos empresariales')