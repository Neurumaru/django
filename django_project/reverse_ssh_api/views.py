from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import *
from django_filters.rest_framework import DjangoFilterBackend
from reverse_ssh_api.serializers import *
from reverse_ssh_api.models import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.exceptions import ErrorDetail

class ReservedPortView(ModelViewSet):
    queryset = ReservedPort.objects.all()
    serializer_class = ReservedPortSerializer

    permission_classes = [
        IsAdminUser
    ]

    def update(self, request, *args, **kwargs):
        return Response(status=HTTP_404_NOT_FOUND)

class UsedPortView(ModelViewSet):
    queryset = UsedPort.objects.all()
    serializer_class = UsedPortSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        user = User.objects.get(username=request.user)
        if serializer.is_valid() and user is not None:
            serializer.save(user=user)
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def list(self, request):
        if request.user.is_superuser:
            queryset =  self.get_queryset()
            serializer = UsedPortAdminSerializer(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            queryset = self.get_queryset().filter(user=self.request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().destroy(request, *args, **kwargs)
        else:
            instance = self.get_object()
            if instance.user == request.user:
                self.perform_destroy(instance)
                return Response(request.data, status=HTTP_204_NO_CONTENT)
            else:
                return Response({'detail': ErrorDetail('You do not have permission to perform this action.', 'permission_denied')}, status=HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        return Response(status=HTTP_404_NOT_FOUND)
    
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