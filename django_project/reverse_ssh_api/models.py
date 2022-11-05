from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class ReservedPort(models.Model):
    reserved_port = models.IntegerField(
        primary_key=True,
        validators=[
            MinValueValidator(1024), 
            MaxValueValidator(65535)
        ]
    )

class UsedPort(models.Model):
    used_port = models.OneToOneField(
        ReservedPort, 
        related_name='used_port', 
        primary_key=True,
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)

class CPUSpec(models.Model):
    used_port = models.OneToOneField(
        UsedPort, 
        related_name='cpu_spec', 
        on_delete=models.CASCADE)
    cpu_arch = models.TextField()
    cpu_bits = models.IntegerField()
    cpu_count = models.IntegerField()
    cpu_arch_string_raw = models.TextField()
    cpu_vendor_id_raw = models.TextField()
    cpu_brand_raw = models.TextField()
    cpu_hz_actural_friendly = models.BigIntegerField()

class CPUStat(models.Model):
    class Meta:
        unique_together = ('used_port', 'cpu_core')

    used_port = models.ForeignKey(
        CPUSpec,
        related_name='cpu_stat', 
        on_delete=models.CASCADE)
    cpu_core = models.IntegerField()
    cpu_percent = models.FloatField()

    cpu_update_time = models.DateTimeField(auto_now=True)

class MemorySpec(models.Model):
    used_port = models.OneToOneField(
        UsedPort, 
        related_name='memory_spec', 
        on_delete=models.CASCADE)
    memory_total = models.BigIntegerField()

class MemoryStat(models.Model):
    used_port = models.OneToOneField(
        MemorySpec, 
        related_name='memory_stat', 
        on_delete=models.CASCADE)

    memory_available = models.BigIntegerField()
    memory_used = models.BigIntegerField()
    memory_free = models.BigIntegerField()
    swap_total = models.BigIntegerField()
    swap_used = models.BigIntegerField()
    swap_free = models.BigIntegerField()

    memory_update_time = models.DateTimeField(auto_now=True)
    
class GPUSpec(models.Model):
    class Meta:
        unique_together = ('used_port', 'gpu_index')

    used_port = models.ForeignKey(
        UsedPort,
        related_name='gpus_spec', 
        on_delete=models.CASCADE)
    gpu_index = models.IntegerField()
    gpu_name = models.TextField()
    gpu_brand = models.TextField()
    gpu_nvml_version = models.TextField()
    gpu_driver_version = models.TextField()
    gpu_vbios_version = models.TextField()
    gpu_multi_gpu_board = models.BooleanField()
    gpu_display_mode = models.BooleanField()
    gpu_display_active = models.BooleanField()
    gpu_persistence_mode = models.BooleanField()
    gpu_compute_mode = models.TextField()
    gpu_power_management_mode = models.BooleanField()
    gpu_power_management_limit = models.IntegerField()
    gpu_enforced_power_limit = models.IntegerField()
    gpu_temperature_shutdown = models.IntegerField()
    gpu_temperature_slowdown = models.IntegerField()

class GPUStat(models.Model):
    used_port = models.OneToOneField(
        GPUSpec, 
        related_name='gpu_stat', 
        on_delete=models.CASCADE)
    
    gpu_power_usage = models.IntegerField()
    gpu_temperature = models.IntegerField()
    gpu_fan_speed = models.IntegerField()

    gpu_clock_info_graphics = models.BigIntegerField()
    gpu_clock_info_sm = models.BigIntegerField()
    gpu_clock_info_mem = models.BigIntegerField()
    gpu_clock_info_video = models.BigIntegerField()

    gpu_memory_info_total = models.BigIntegerField()
    gpu_memory_info_free = models.BigIntegerField()
    gpu_memory_info_used = models.BigIntegerField()

    gpu_bar1_memory_info_total = models.BigIntegerField()
    gpu_bar1_memory_info_free = models.BigIntegerField()
    gpu_bar1_memory_info_used = models.BigIntegerField()

    gpu_utilization_gpu = models.IntegerField()
    gpu_utilization_memory = models.IntegerField()
    gpu_utilization_encoder = models.IntegerField()
    gpu_utilization_decoder = models.IntegerField()

    gpu_update_time = models.DateTimeField(auto_now=True)