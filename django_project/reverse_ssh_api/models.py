from doctest import master
from django.db import models

class ReservedPort(models.Model):
    reserved_port = models.IntegerField(primary_key=True)

class UsedPort(models.Model):
    used_port = models.OneToOneField(
        ReservedPort, 
        related_name='used_port', 
        primary_key=True,
        on_delete=models.CASCADE)

class CPU(models.Model):
    port = models.OneToOneField(
        UsedPort, 
        related_name='cpu', 
        on_delete=models.CASCADE)
    cpu_name = models.CharField(max_length=512)
    cpu_clock = models.FloatField()
    cpu_count = models.IntegerField()

class RAM(models.Model):
    port = models.OneToOneField(
        UsedPort, 
        related_name='ram', 
        on_delete=models.CASCADE)
    ram_total_size = models.IntegerField()
    ram_free_size = models.IntegerField()
    ram_used_size = models.IntegerField()
    
class GPU(models.Model):
    port = models.ForeignKey(
        UsedPort,
        related_name='gpus', 
        on_delete=models.CASCADE)
    gpu_name = models.CharField(max_length=512)
    gpu_total_size = models.IntegerField()
    gpu_free_size = models.IntegerField()
    gpu_used_size = models.IntegerField()