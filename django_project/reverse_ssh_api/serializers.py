from rest_framework import serializers
from .models import *

class ReservedPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservedPort
        fields = ['reserved_port']

class UsedPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedPort
        fields = ['used_port']

class CPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPU
        fields = ['id', 'port', 'cpu_name', 'cpu_clock', 'cpu_count']

class RAMSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAM
        fields = ['id', 'port', 'ram_total_size', 'ram_free_size', 'ram_used_size']

class GPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPU
        fields = ['id', 'port', 'gpu_name', 'gpu_total_size', 'gpu_free_size', 'gpu_used_size']
