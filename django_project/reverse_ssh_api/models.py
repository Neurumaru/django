from django.db import models

class ReservedPort(models.Model):
    port = models.IntegerField()

class Connection(models.Model):
    port = models.ForeignKey(ReservedPort, on_delete=models.DO_NOTHING)
    stat = models.JSONField()
