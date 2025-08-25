from django.forms.models import model_to_dict

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

    parametros = {}

    try:
        for filtro in filtros.values():
            if filtro["tipo"] == "data":
                parametros[filtro["variavel"]] = "2000-01-01"
            elif filtro["tipo"] == "empresa":
                parametros[filtro["variavel"]] = "0"
            elif filtro["tipo"] == "numero":
                parametros[filtro["variavel"]] = "0"
            elif filtro["tipo"] == "texto":
                parametros[filtro["variavel"]] = ""

    except:  # noqa: E722
        print(model_to_dict(filtros))

    with engine.connect() as conn:
        colunas = conn.execute(statement=text(query), parameters=parametros)

    colunas_list = []

    for coluna in colunas.keys():
        colunas_list.append(coluna)

    return colunas_list


def somar_coluna(grupo, colunas):
    tot = {}
    for c in colunas:
        if c.totalizar:
            tot[c.coluna] = sum(float(l[c.coluna].replace(",", ".")) for l in grupo)
        else:
            tot[c.coluna] = ""
    return tot
