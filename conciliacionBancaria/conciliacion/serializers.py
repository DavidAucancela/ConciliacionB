from rest_framework import serializers
from .models import TransaccionBancarias
from .models import Cuenta

class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionBancarias
        fields = '__all__'

class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = '__all__'  

