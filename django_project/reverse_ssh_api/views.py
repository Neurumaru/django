from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import *
from django_filters.rest_framework import DjangoFilterBackend
from reverse_ssh_api.serializers import *
from reverse_ssh_api.models import *

class ReservedPortView(ModelViewSet):
    queryset = ReservedPort.objects.all()
    serializer_class = ReservedPortSerializer

    permission_classes = [
        IsAdminUser
    ]

class UsedPortView(ModelViewSet):
    queryset = UsedPort.objects.all()
    serializer_class = UsedPortSerializer
    
class FreePortView(ModelViewSet):
    queryset = ReservedPort.objects.all().difference(UsedPort.objects.all())
    serializer_class = ReservedPortSerializer

class CPUView(ModelViewSet):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['used_port']

class RAMView(ModelViewSet):
    queryset = RAM.objects.all()
    serializer_class = RAMSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['used_port']

class GPUView(ModelViewSet):
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['used_port', 'gpu_index']