from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Setores(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):  # type: ignore
        return self.nome


class Relatorios(models.Model):
    nome = models.CharField(max_length=255)
    setores = models.ForeignKey(Setores, on_delete=models.SET_DEFAULT, default=1)
    query = models.CharField(max_length=255)

    def __str__(self):  # type: ignore
        return self.nome


class Filtros(models.Model):
    exibicao = models.CharField(max_length=255)
    variavel = models.CharField(max_length=255)
    relatorio = models.ForeignKey(Relatorios, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=255)

    def __str__(self):  # type: ignore
        return self.exibicao


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255, default="vazio")
    setor = models.ManyToManyField(Setores)
    relatorios = models.ManyToManyField(Relatorios)

    def __str__(self):  # type: ignore
        return f"{self.user.username} ({self.setor})"  # type: ignore


class Logs(models.Model):
    responsavel = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=255)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # type: ignore
        return f"{self.responsavel.nome} - {self.acao} - {self.data.strftime('%d/%m/%Y %H:%M:%S')}"  # type: ignore


class Empresa(models.Model):
    codigo_interno = models.IntegerField()
    nome = models.CharField(max_length=150)

    def __str__(self):  # type: ignore
        return f"{self.nome}"
