import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from administrador.models import Logs


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
    engine = create_engine(str(uri))
    with engine.connect() as conn:
        try:
            sql_data = conn.execute(sql, params)
        except:  # noqa: E722
            sql_data = conn.execute(sql)

        dados = pd.DataFrame(sql_data.fetchall(), columns=sql_data.keys())  # type: ignore

        print(sql_data.keys())

        return dados


def format_numbers(x):
    try:
        # tenta converter para float, se der certo formata com ","
        float(x)
        return str(x).replace(".", ",")
    except (ValueError, TypeError):
        return x


def verificar_colunas(query: str, filtros):
    load_dotenv()
    uri = os.getenv("DATABASE_URI")

    engine = create_engine(str(uri))

    try:
        for filtro in filtros:
            if filtro["tipo"] == "data":
                query = query.replace(f":{filtro.variavel}", "2025-06-01")
            elif filtro["tipo"] == "empresa":
                query = query.replace(f":{filtro.variavel}", "46455")
            elif filtro["tipo"] == "numero":
                query = query.replace(f":{filtro.variavel}", "0")
            elif filtro["tipo"] == "texto":
                query = query.replace(f":{filtro.variavel}", "")

    except:
        print(filtros)

    with engine.connect() as conn:
        colunas = conn.execute(text(query))

    return colunas.keys()
