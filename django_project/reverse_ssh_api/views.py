from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import *
from django_filters.rest_framework import DjangoFilterBackend
from reverse_ssh_api.serializers import *
from reverse_ssh_api.models import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.status import \
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, \
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, AuthenticationFailed

# ====================================================================================================
# ReservedPortView
# - GET /api/reserved-ports/
# - POST /api/reserved-ports/
# - DELETE /api/reserved-ports/<pk>/
# ====================================================================================================
class ReservedPortView(ModelViewSet):
    queryset = ReservedPort.objects.all()
    serializer_class = ReservedPortSerializer

    # ====================================================================================================
    # Authentication
    # - Only superuser can access the reserved port API
    # ====================================================================================================
    permission_classes = [IsAdminUser]

    # ====================================================================================================
    # UPDATE /api/reserved-ports/<pk>/
    # - Method not allowed
    # ====================================================================================================
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

# ====================================================================================================
# UsedPortView
# - GET /api/used-ports/
# - POST /api/used-ports/
# - DELETE /api/used-ports/<pk>/
# ====================================================================================================
class UsedPortView(ModelViewSet):
    queryset = UsedPort.objects.all()
    serializer_class = UsedPortSerializer
    
    # ====================================================================================================
    # Authentication
    # - Suepruser can access all used ports
    # - User can only access their own used ports
    # ====================================================================================================

    # ====================================================================================================
    # POST /api/used-ports/
    # - Add request.user to the serializer
    # ====================================================================================================
    def create(self, request):
        # Get user from request
        user = User.objects.get(username=request.user)
        if user is None:
            raise AuthenticationFailed()

        # Validate request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Add user to the serializer
        serializer.save(user=user)

        return Response(serializer.data, status=HTTP_201_CREATED)

    # ====================================================================================================
    # GET /api/used-ports/
    # - Superuser can access all used ports
    # - User can only access their own used ports
    # ====================================================================================================
    def list(self, request):
        # Superuser can access all used ports
        if request.user.is_superuser:
            queryset =  self.get_queryset()
            serializer = UsedPortAdminSerializer(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        # User can only access their own used ports
        else:
            queryset = self.get_queryset().filter(user=self.request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

    # ====================================================================================================
    # DELETE /api/used-ports/<pk>/
    # - Superuser can delete any used port
    # - User can only delete their own used port
    # ====================================================================================================
    def destroy(self, request, *args, **kwargs):
        # Superuser can delete any used port
        if request.user.is_superuser:
            return super().destroy(request, *args, **kwargs)

        # User can only delete their own used port
        else:
            # Check if the user is the owner of the used port
            instance = self.get_object()
            if instance.user == request.user:
                return super().destroy(request, *args, **kwargs)
            else:
                raise PermissionDenied()

    # ====================================================================================================
    # UPDATE /api/used-ports/<pk>/
    # - Method not allowed
    # - If user is not the own of the used port, raise PermissionDenied
    # ====================================================================================================
    def update(self, request, *args, **kwargs):
        if request.user.is_superuser:
            raise MethodNotAllowed(request.method)
        else:
            instance = self.get_object()
            if instance.user == request.user:
                raise MethodNotAllowed(request.method)
            else:
                raise PermissionDenied()
    
# ====================================================================================================
# FreePortView
# - GET /api/free-ports/
# ====================================================================================================
class FreePortView(ModelViewSet):
    queryset = ReservedPort.objects.values('reserved_port').difference(UsedPort.objects.values('used_port'))
    serializer_class = ReservedPortSerializer

    # ====================================================================================================
    # Authentication
    # - Superuser and user can access all free ports
    # ====================================================================================================

    # ====================================================================================================
    # POST /api/free-ports/
    # - Method not allowed
    # ====================================================================================================
    def create(self, request):
        raise MethodNotAllowed(request.method)

    # ====================================================================================================
    # DELETE /api/free-ports/<pk>/
    # - Method not allowed
    # ====================================================================================================
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    # ====================================================================================================
    # PUT /api/free-ports/<pk>/
    # - Method not allowed
    # ====================================================================================================
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

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