from rest_framework import viewsets
from rest_framework.permissions import *
from django_filters.rest_framework import DjangoFilterBackend
from reverse_ssh_api.serializers import *
from reverse_ssh_api.models import *

class ReservedPortView(viewsets.ModelViewSet):
    queryset = ReservedPort.objects.all()
    serializer_class = ReservedPortSerializer

    permission_classes = [
        IsAdminUser
    ]

class UsedPortView(viewsets.ModelViewSet):
    queryset = UsedPort.objects.all()
    serializer_class = UsedPortSerializer
    
class FreePortView(viewsets.ModelViewSet):
    queryset = ReservedPort.objects.all().difference(UsedPort.objects.all())
    serializer_class = ReservedPortSerializer

class CPUView(viewsets.ModelViewSet):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['used_port']

class RAMView(viewsets.ModelViewSet):
    queryset = RAM.objects.all()
    serializer_class = RAMSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['used_port']

class GPUView(viewsets.ModelViewSet):
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['used_port', 'gpu_index']