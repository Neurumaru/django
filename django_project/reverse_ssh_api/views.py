from rest_framework import viewsets
from reverse_ssh_api.serializers import *
from reverse_ssh_api.models import *

class ReservedPortView(viewsets.ModelViewSet):
    queryset = ReservedPort.objects.all()
    serializer_class = ReservedPortSerializer

class UsedPortView(viewsets.ModelViewSet):
    queryset = UsedPort.objects.all()
    serializer_class = UsedPortSerializer

class CPUView(viewsets.ModelViewSet):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer

class RAMView(viewsets.ModelViewSet):
    queryset = RAM.objects.all()
    serializer_class = RAMSerializer

class GPUView(viewsets.ModelViewSet):
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer