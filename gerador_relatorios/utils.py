from django.db import connection
from administrador.models import Logs


def registrar_log(usuario, acao):
    try:
        Logs.objects.create(responsavel=usuario, acao=acao)
    except Exception as e:
        print("Erro ao registrar log:", e)


def ler_log(log: Logs):
    data = log.data.strftime("%d/%m/%Y %H:%M")
    return f"{log.responsavel} - {log.acao} - " + data


def executar_query(relatorio, filtros, using='banco_remoto'):
    sql = relatorio.query # considerando que você tem um campo "sql" no modelo
    params = filtros

    with connection[using].cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
