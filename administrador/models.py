from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Setores(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Relatorios(models.Model):
    nome = models.CharField(max_length=100)
    query = models.TextField()
    setores = models.ForeignKey(Setores, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Filtros(models.Model):
    TIPO_CHOICES = [
        ("texto", "Texto"),
        ("numero", "Número"),
        ("data", "Data"),
        ("empresa", "Empresa"),
    ]

    relatorio = models.ForeignKey(
        Relatorios, on_delete=models.CASCADE, related_name="filtros"
    )
    exibicao = models.CharField(max_length=100)
    variavel = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.exibicao} ({self.variavel})"


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


class Colunas(models.Model):
    coluna = models.CharField()
    relatorio = models.ForeignKey(Relatorios, on_delete=models.CASCADE, null=False)
    ordem = models.IntegerField(null=True)
    largura = models.IntegerField(null=True)
    agrupamento = models.BooleanField(default=False)
    totalizar = models.BooleanField(default=False)
    visibilidade = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.coluna}"
