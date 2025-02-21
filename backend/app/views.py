#from django.shortcuts import render

from rest_framework import viewsets
from .models import Item
from .serializers import TransaccionSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = TransaccionSerializer
