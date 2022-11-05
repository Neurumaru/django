from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import *
from django_filters.rest_framework import DjangoFilterBackend
from reverse_ssh_api.serializers import *
from reverse_ssh_api.models import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

class ReservedPortView(ModelViewSet):
    queryset = ReservedPort.objects.all()
    serializer_class = ReservedPortSerializer

    permission_classes = [
        IsAdminUser
    ]

class UsedPortView(ModelViewSet):
    queryset = UsedPort.objects.all()
    serializer_class = UsedPortSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        user = User.objects.get(username=request.user)
        if serializer.is_valid() and user is not None:
            serializer.save(user=user)
            return Response(status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

    def list(self, request):
        if request.user.is_superuser:
            queryset =  self.get_queryset()
            serializer = UsedPortAdminSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = self.get_queryset().filter(user=self.request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
    
class FreePortView(ModelViewSet):
    queryset = ReservedPort.objects.values('reserved_port').difference(UsedPort.objects.values('used_port'))
    serializer_class = ReservedPortSerializer

# class CPUView(ModelViewSet):
#     queryset = CPU.objects.all()
#     serializer_class = CPUSerializer

#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['used_port']

# class RAMView(ModelViewSet):
#     queryset = RAM.objects.all()
#     serializer_class = RAMSerializer

#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['used_port']

# class GPUView(ModelViewSet):
#     queryset = GPU.objects.all()
#     serializer_class = GPUSerializer

#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['used_port', 'gpu_index']