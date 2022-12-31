from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import *
from reverse_ssh_api.serializers import *
from reverse_ssh_api.models import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.status import \
    HTTP_200_OK, HTTP_201_CREATED
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, AuthenticationFailed, ValidationError


# ====================================================================================================
# ReservedPortView
# - GET /api/reserved-port/
# - POST /api/reserved-port/
# - DELETE /api/reserved-port/<pk>/
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
    # UPDATE /api/reserved-port/<pk>/
    # - Method not allowed
    # ====================================================================================================
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)


# ====================================================================================================
# UsedPortView
# - GET /api/used-port/
# - POST /api/used-port/
# - DELETE /api/used-port/<pk>/
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
    # POST /api/used-port/
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
    # GET /api/used-port/
    # - Superuser can access all used ports
    # - User can only access their own used ports
    # ====================================================================================================
    def list(self, request):
        # Superuser can access all used ports
        if request.user.is_superuser:
            queryset = self.get_queryset()
            serializer = UsedPortAdminSerializer(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        # User can only access their own used ports
        else:
            queryset = self.get_queryset().filter(user=self.request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

    # ====================================================================================================
    # DELETE /api/used-port/<pk>/
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
    # UPDATE /api/used-port/<pk>/
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
# - GET /api/free-port/
# ====================================================================================================
class FreePortView(ModelViewSet):
    queryset = ReservedPort.objects.values('reserved_port').difference(UsedPort.objects.values('used_port'))
    serializer_class = ReservedPortSerializer

    # ====================================================================================================
    # Authentication
    # - Superuser and user can access all free ports
    # ====================================================================================================

    # ====================================================================================================
    # POST /api/free-port/
    # - Method not allowed
    # ====================================================================================================
    def create(self, request):
        raise MethodNotAllowed(request.method)

    # ====================================================================================================
    # DELETE /api/free-port/<pk>/
    # - Method not allowed
    # ====================================================================================================
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    # ====================================================================================================
    # PUT /api/free-port/<pk>/
    # - Method not allowed
    # ====================================================================================================
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)


# ====================================================================================================
# CPUSpecView
# - GET /api/cpu-spec/
# - POST /api/cpu-spec/
# ====================================================================================================
class CPUSpecView(ModelViewSet):
    queryset = CPUSpec.objects.all()
    serializer_class = CPUSpecSerializer

    # ====================================================================================================
    # Authentication
    # - Superuser can access all CPU specs
    # - User can only access their own CPU specs
    # ====================================================================================================

    # ====================================================================================================
    # POST /api/cpu-spec/
    # - Check if the user has used port
    # ====================================================================================================
    def create(self, request):
        # Get user from request
        request_user = User.objects.get(username=request.user)
        if request_user is None:
            raise AuthenticationFailed()

        used_port = UsedPort.objects.filter(used_port=request.data['used_port'])
        if len(used_port) != 1:
            raise ValidationError({'used_port': ['Used port does not exist']})

        used_port_user = used_port[0].user
        if used_port_user is None or request_user != used_port_user:
            raise PermissionDenied()

        return super().create(request)

    # ====================================================================================================
    # GET /api/cpu-spec/
    # - Superuser can access all CPU specs
    # - User can only access their own CPU specs
    # ====================================================================================================
    def list(self, request):
        # User Authentication
        request_user = User.objects.get(username=request.user)
        if request_user is None:
            raise AuthenticationFailed()

        # Superuser can access all CPU specs
        if request_user.is_superuser:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        # User can only access their own CPU specs
        else:
            queryset = CPUSpec.objects.select_related('used_port').filter(used_port__user=request_user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

    # ====================================================================================================
    # DELETE /api/cpu-spec/<pk>/
    # - Method not allowed
    # ====================================================================================================
    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser:
            raise MethodNotAllowed(request.method)
        else:
            if self.get_object().used_port.user == request.user:
                raise MethodNotAllowed(request.method)
            else:
                raise PermissionDenied()

    # ====================================================================================================
    # PUT /api/cpu-spec/<pk>/
    # - Method not allowed
    # ====================================================================================================
    def update(self, request, *args, **kwargs):
        if request.user.is_superuser:
            raise MethodNotAllowed(request.method)
        else:
            if self.get_object().used_port.user == request.user:
                raise MethodNotAllowed(request.method)
            else:
                raise PermissionDenied()

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
