from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from reverse_ssh_api.validators import ValueInListValidator

# ====================================================================================================
# ReservedPort
# - reserved_port: Reserved port for reverse SSH
#   - Type: Integer (1024 ~ 65535)
#   - Primary key
# ====================================================================================================
class ReservedPort(models.Model):
    reserved_port = models.IntegerField(
        primary_key=True,
        validators=[
            MinValueValidator(1024), 
            MaxValueValidator(65535)
        ]
    )

# ====================================================================================================
# UsedPort
# - used_port: Used port for reverse SSH
#   - Type: OneToOneFiled (ReservedPort)
#     - On delete: CASCADE
#   - Primary key
# - user: User who uses the port
#   - Type: ForeignKey (User)
#     - On delete: CASCADE
#   - Index
# ====================================================================================================
class UsedPort(models.Model):
    used_port = models.OneToOneField(
        ReservedPort, 
        primary_key=True,
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        related_name='used_port',
        on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

# ====================================================================================================
# CPUSpec
# - used_port: Used port for reverse SSH
#   - Type: OneToOneFiled (UsedPort)
#     - On delete: CASCADE
#   - Index
# - cpu_arch: CPU architecture
#   - Type: TextField
# - cpu_bits: CPU bits
#   - Type: Integer (32, 64)
# - cpu_count: CPU count
#   - Type: Integer (1 ~ 128)
# - cpu_arch_string_raw: CPU architecture string (raw)
#   - Type: TextField
# - cpu_vender_id_raw: CPU vender ID (raw)
#   - Type: TextField
# - cpu_brand_raw: CPU brand (raw)
#   - Type: TextField
# - cpu_hz_actual_friendly: CPU frequency
#   - Type: BigIntegerField
# ====================================================================================================
class CPUSpec(models.Model):
    used_port = models.OneToOneField(
        UsedPort,
        on_delete=models.CASCADE)
    cpu_arch = models.TextField()
    cpu_bits = models.IntegerField(
        validators=[
            ValueInListValidator([32, 64])
        ]
    )
    cpu_count = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(128)
        ]
    )
    cpu_arch_string_raw = models.TextField()
    cpu_vendor_id_raw = models.TextField()
    cpu_brand_raw = models.TextField()
    cpu_hz_actural_friendly = models.BigIntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['used_port']),
        ]

# ====================================================================================================
# CPUStat
# - cpu_spec: CPU specification
#   - Type: ForeignKey (CPUSpec)
#     - On delete: CASCADE
#   - Index
# - cpu_core: CPU core
#   - Type: Integer (0 ~ 127)
# - cpu_percent: CPU usage
#   - Type: Float (0.0 ~ 100.0)
# - cpu_update_time: CPU usage update time
#   - Type: DateTimeField (auto_now=True)
#   - Index
# - used_port & cpu_core: unique key
# ====================================================================================================
class CPUStat(models.Model):
    cpu_spec = models.ForeignKey(
        CPUSpec,
        on_delete=models.CASCADE)
    cpu_core = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(127)
        ]
    )
    cpu_percent = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ]
    )

    cpu_update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cpu_spec', 'cpu_core')
        indexes = [
            models.Index(fields=['cpu_spec']),
            models.Index(fields=['cpu_update_time']),
        ]


# ====================================================================================================
# MemorySpec
# - used_port: Used port for reverse SSH
#   - Type: OneToOneFiled (UsedPort)
#     - On delete: CASCADE
#   - Index
# - mem_total: Total memory
#   - Type: BigIntegerField
# ====================================================================================================
class MemorySpec(models.Model):
    used_port = models.OneToOneField(
        UsedPort, 
        on_delete=models.CASCADE)
    memory_total = models.BigIntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['used_port']),
        ]

# ====================================================================================================
# MemoryStat
# - memory_spec: Memory specification
#   - Type: OneToOneField (MemorySpec)
#     - On delete: CASCADE
# - memory_available: Available memory
#   - Type: BigIntegerField
# - memory_used: Used memory
#   - Type: BigIntegerField
# - memory_free: Free memory
#   - Type: BigIntegerField
# - swap_total: Total swap
#   - Type: BigIntegerField
# - swap_used: Used swap
#   - Type: BigIntegerField
# - swap_free: Free swap
#   - Type: BigIntegerField
# - mem_update_time: Memory usage update time
#   - Type: DateTimeField (auto_now=True)
#   - Index
# ====================================================================================================
class MemoryStat(models.Model):
    memory_spec = models.OneToOneField(
        MemorySpec, 
        on_delete=models.CASCADE)

    memory_available = models.BigIntegerField()
    memory_used = models.BigIntegerField()
    memory_free = models.BigIntegerField()
    swap_total = models.BigIntegerField()
    swap_used = models.BigIntegerField()
    swap_free = models.BigIntegerField()

    memory_update_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['memory_spec']),
            models.Index(fields=['memory_update_time']),
        ]
    
# ====================================================================================================
# GPUSpec
# - used_port: Used port for reverse SSH
#   - Type: ForeignKey (UsedPort)
#     - On delete: CASCADE
#   - Index
# - gpu_index: GPU index
#   - Type: Integer (0 ~ 3)
# - gpu_name: GPU name
#   - Type: TextField
# - gpu_brand: GPU brand
#   - Type: TextField
# - gpu_nvml_version: GPU NVML version
#   - Type: TextField
# - gpu_driver_version: GPU driver version
#   - Type: TextField
# - gpu_vbios_version: GPU VBIOS version
#   - Type: TextField
# - gpu_multi_gpu_board: GPU multi GPU board
#   - Type: BooleanField
# - gpu_display_mode: GPU display mode
#   - Type: BooleanField
# - gpu_display_active: GPU display active
#   - Type: BooleanField
# - gpu_persistence_mode: GPU persistence mode
#   - Type: BooleanField
# - gpu_compute_mode: GPU compute mode
#   - Type: TextField
# - gpu_power_management_mode: GPU power management mode
#   - Type: BooleanField
# - gpu_power_management_limit: GPU power management limit
#   - Type: Integer
# - gpu_enforced_power_limit: GPU enforced power limit
#   - Type: Integer
# - gpu_temperature_shutdown: GPU temperature shutdown
#   - Type: Integer
# - gpu_temperature_slowdown: GPU temperature slowdown
#   - Type: Integer
# ====================================================================================================
class GPUSpec(models.Model):
    used_port = models.ForeignKey(
        UsedPort,
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

    class Meta:
        unique_together = ('used_port', 'gpu_index')
        indexes = [
            models.Index(fields=['used_port']),
        ]

# ====================================================================================================
# GPUStat
# - gpu_spec: GPU specification
#   - Type: OneToOneField (GPUSpec)
#     - On delete: CASCADE
#   - Index
# - gpu_power_usage: GPU power usage
#   - Type: Integer
# - gpu_temperature: GPU temperature
#   - Type: Integer
# - gpu_fan_speed: GPU fan speed
#   - Type: Integer
# - gpu_clock_info_graphics: GPU clock info graphics
#   - Type: BigIntegerField
# - gpu_clock_info_sm: GPU clock info SM
#   - Type: BigIntegerField
# - gpu_clock_info_mem: GPU clock info memory
#   - Type: BigIntegerField
# - gpu_clock_info_video: GPU clock info video
#   - Type: BigIntegerField
# - gpu_memory_info_total: GPU memory info total
#   - Type: BigIntegerField
# - gpu_memory_info_free: GPU memory info free
#   - Type: BigIntegerField
# - gpu_memory_info_used: GPU memory info used
#   - Type: BigIntegerField
# - gpu_bar1_memory_info_total: GPU BAR1 memory info total
#   - Type: BigIntegerField
# - gpu_bar1_memory_info_free: GPU BAR1 memory info free
#   - Type: BigIntegerField
# - gpu_bar1_memory_info_used: GPU BAR1 memory info used
#   - Type: BigIntegerField
# - gpu_utilization_gpu: GPU utilization GPU
#   - Type: Integer
# - gpu_utilization_memory: GPU utilization memory
#   - Type: Integer
# - gpu_utilization_encoder: GPU utilization encoder
#   - Type: Integer
# - gpu_utilization_decoder: GPU utilization decoder
#   - Type: Integer
# - gpu_update_time: GPU update time
#   - Type: DateTimeField (auto_now=True)
#   - Index
# ====================================================================================================
class GPUStat(models.Model):
    gpu_spec = models.OneToOneField(
        GPUSpec, 
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
    
    class Meta:
        indexes = [
            models.Index(fields=['gpu_spec']),
            models.Index(fields=['gpu_update_time']),
        ]