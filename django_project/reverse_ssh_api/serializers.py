from rest_framework import serializers
from reverse_ssh_api.models import *

# ====================================================================================================
# ReservedPortSerializer
# ====================================================================================================
class ReservedPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservedPort
        fields = ['reserved_port']

# ====================================================================================================
# UsedPortSerializer (for user)
# ====================================================================================================
class UsedPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedPort
        fields = ['used_port']

# ====================================================================================================
# UsedPortSerializer (for superuser)
# - Add user field to the read-only fields
# ====================================================================================================
class UsedPortAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = UsedPort
        fields = ['used_port', 'user', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'user': {'read_only': True}
        }

# ====================================================================================================
# CPUSpecSerializer
# ====================================================================================================
class CPUSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPUSpec
        fields = ['id', 'used_port', 'cpu_arch', 'cpu_bits', 'cpu_count', 'cpu_arch_string_raw', 'cpu_vendor_id_raw', 'cpu_brand_raw', 'cpu_hz_actural_friendly']


# class CPUSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CPU
#         fields = ['id', 'used_port', 'cpu_name', 'cpu_clock', 'cpu_count']

# class RAMSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RAM
#         fields = ['id', 'used_port', 'ram_total_size', 'ram_free_size', 'ram_used_size']

# class GPUSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GPU
#         fields = ['id', 'used_port', 'gpu_index', 'gpu_name', 'gpu_total_size', 'gpu_free_size', 'gpu_used_size']
