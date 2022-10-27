from rest_framework import serializers
from .models import ReservedPort, Connection

class ReservedPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservedPort
        fields = ['port']

class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fileds = ['port', 'stat']
