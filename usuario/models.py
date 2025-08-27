from django.db import models
from administrador.models import Perfil, Relatorios


# Create your models here.
class Agendamentos(models.Model):

    METODO_CHOICES = [("dia", "Diario"), ("semana", "Semanal"), ("mes", "Mensal")]

    relatorio = models.ForeignKey(
        Relatorios, on_delete=models.CASCADE, null=False, related_name="agendamento"
    )
    metodo = models.CharField(choices=METODO_CHOICES)
    intervalo = models.IntegerField(null=False, default=1)
    usuario = models.ForeignKey(
        Perfil, on_delete=models.CASCADE, null=False, name="usuario"
    )
    beneficiados = models.ManyToManyField(
        Perfil, null=False, related_name="beneficiarios"
    )
