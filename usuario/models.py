from django.db import models
from administrador.models import Filtros, Perfil, Relatorios


# Create your models here.
class Agendamentos(models.Model):

    METODO_CHOICES = [("dia", "Diario"), ("semana", "Semanal"), ("mes", "Mensal")]

    relatorio = models.ForeignKey(
        Relatorios, on_delete=models.CASCADE, null=False, related_name="agendamento"
    )
    metodo = models.CharField(choices=METODO_CHOICES, max_length=255)
    intervalo = models.IntegerField(null=False)
    usuario = models.ForeignKey(Perfil, on_delete=models.CASCADE, name="usuario")
    beneficiados = models.ManyToManyField(Perfil, related_name="beneficiarios")
    filtros = models.ManyToManyField(Filtros, related_name="filtros")


class FiltrosPreenchimento(models.Model):
    agendamento = models.ForeignKey(
        Agendamentos, on_delete=models.CASCADE, related_name="agendamento"
    )
    filtro = models.ForeignKey(
        Filtros, on_delete=models.CASCADE, related_name="parametros"
    )
    preenchimento = models.CharField(max_length=255)
