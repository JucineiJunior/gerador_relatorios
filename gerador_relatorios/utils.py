from sqlalchemy import create_engine, text
from administrador.models import Logs
import pandas as pd

def registrar_log(usuario, acao):
    try:
        Logs.objects.create(responsavel=usuario, acao=acao)  # type: ignore
    except Exception as e:
        print("Erro ao registrar log:", e)


def ler_log(log: Logs):
    data = log.data.strftime("%d/%m/%Y %H:%M")  # type: ignore
    return f"{log.responsavel} - {log.acao} - " + data


def executar_query(relatorio, filtros):
    sql = text(relatorio.query)  # considerando que você tem um campo "sql" no modelo
    params = filtros
    engine = create_engine(
         "postgresql+psycopg2://rede_trevo_read:x6gqt0OS5BcAdJuu7RF4U9iEOsAskE36@db.clientes-externos.qualityautomacao.com.br:6432/redetrevo"
    )
    with engine.connect() as cursor:
        try:
            sql_data = cursor.execute(sql, params)
        except:
            sql_data = cursor.execute(sql)

        dados = pd.DataFrame(sql_data.fetchall(), columns=sql_data.keys()) # type: ignore
        return dados
