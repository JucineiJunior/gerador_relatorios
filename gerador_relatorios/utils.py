from sqlalchemy import create_engine, text
from administrador.models import Logs
import pandas as pd
from dotenv import load_dotenv
import os


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
    load_dotenv()
    uri = os.getenv("DATABASE_URI")
    engine = create_engine(uri)  # type: ignore
    with engine.connect() as cursor:
        sql_data = cursor.execute(sql, params)
        dados = pd.DataFrame(sql_data.fetchall(), columns=sql_data.keys())  # type: ignore
        return dados
