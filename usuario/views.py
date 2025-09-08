from datetime import datetime, date
from itertools import groupby
from io import StringIO
from weasyprint import HTML
import pandas as pd

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.core.mail import send_mail

from administrador.models import Empresa, Filtros, Perfil, Relatorios, Setores, Colunas
from gerador_relatorios.utils import executar_query, format_numbers, somar_coluna
from usuario.forms import AgendamentoForm, SugestaoForm

# Create your views here.


@login_required
def home_view(request):
    user = request.user
    perfil = get_object_or_404(Perfil, user=user.id)
    setores_usuario = perfil.setor.all()

    setor_nome = request.GET.get("setores")
    relatorio_id = request.GET.get("relatorio")

    relatorios = None
    filtros = None
    setor_selecionado = None
    relatorio = None
    empresas = None

    if relatorio_id:
        # Mostrar filtros do relatório
        relatorio = get_object_or_404(Relatorios, id=relatorio_id)
        filtros = Filtros.objects.filter(relatorio=relatorio.id)  # type: ignore
        empresas = Empresa.objects.all().values()  # type: ignore
    if setor_nome:
        # Filtrar relatórios por setor, se o setor for do usuário
        setor_selecionado = get_object_or_404(
            Setores,
            nome=setor_nome,
            id__in=setores_usuario.values_list("id", flat=True),
        )
        relatorios = Relatorios.objects.filter(setores=setor_selecionado)  # type: ignore

    else:
        # Mostrar todos os relatórios dos setores do usuário
        relatorios = Relatorios.objects.filter(setores__in=setores_usuario).distinct()  # type: ignore

    context = {
        "setores": setores_usuario,
        "relatorios": relatorios,
        "filtros": filtros,
        "relatorio_selecionado": relatorio,
        "setor_selecionado": setor_selecionado,
        "empresas": empresas,
    }
    return render(request, "home.html", context)


def gerar_relatorio(request, relatorio_id):
    relatorio = get_object_or_404(Relatorios, id=relatorio_id)
    filtros = Filtros.objects.filter(relatorio=relatorio_id)  # type: ignore

    filtros = list(filtros.values())

    # Inicializa variáveis
    resultados = []
    filtros_request = {}
    parametros = {}

    if request.method == "POST":
        # Extrai filtros do request.POST (ajuste conforme seus campos)
        filtros_request = request.POST.dict()
        for filtro in filtros:
            for dado in filtros_request:
                if filtro["exibicao"] == dado or filtro["variavel"] == dado:
                    parametros[filtro["variavel"]] = filtros_request[dado]

        resultados = executar_query(relatorio, parametros)

        resultados = pd.DataFrame(
            resultados.map(format_numbers, old=".", new=",")  # type: ignore
        )
        try:
            for data in resultados.select_dtypes(include="datetime64[ns]").columns:
                resultados[data] = resultados[data].dt.strftime("%Y-%m-%d")
        except:  # noqa: E722
            pass
        request.session["relatorio_gerado"] = resultados.to_json(date_format="iso")
        request.session["relatorio_nome"] = relatorio.nome
        request.session["filtros"] = filtros
        request.session["filtros_gerados"] = parametros
        request.session["relatorio_id"] = relatorio.id  # type: ignore
    context = {
        "relatorio": relatorio,
        "filtros": filtros,  # Envia os filtros usados de volta para o template
        "resultados": resultados.to_html(index=False, classes="table table-striped table-dark text-light table-bordered border-white rounded").replace("None", "").replace("NaN", ""),  # type: ignore
    }

    return render(request, "relatorios/gerar.html", context)


def download_manager(request, formato):
    df_json = StringIO(request.session.get("relatorio_gerado"))
    nome = request.session.get("relatorio_nome")
    filtros = request.session.get("filtros")
    filtros_atuais = request.session.get("filtros_gerados")

    relatorio_id = request.session.get("relatorio_id")
    colunas = Colunas.objects.filter(relatorio=relatorio_id).order_by("ordem")  # type: ignore

    ordem_colunas = [c.coluna for c in colunas]
    agrupados = [c.coluna for c in colunas if c.agrupamento]

    if not df_json:
        return HttpResponse(status=404)

    df = pd.read_json(df_json)

    df = df[ordem_colunas]

    for coluna in colunas:
        if not coluna.visibilidade:
            df = df.drop(columns=coluna.coluna)
            colunas = colunas.exclude(pk=coluna.id)  # type: ignore

    for k, v in filtros_atuais.items():
        if k == "empresa" and v == 0:
            filtros_atuais[k] == "Todas"  # type: ignore
        try:
            v = datetime.strptime(v, "%d-%m-%Y").date()  # type: ignore
            filtros_atuais[k] = v.strftime("%d/%m/%Y")
        except Exception:
            pass

    if formato == "csv":
        df = df.map(format_numbers, old=",", new=".")  # type: ignore
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f"attachment; filename={nome.capitalize()}.csv"
        )
        df.to_csv(response, index=False)  # type: ignore
    elif formato == "xlsx":
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename={nome.capitalize()}.xlsx"
        )
        with pd.ExcelWriter(response, engine="xlsxwriter") as writer:  # type: ignore
            df.to_excel(writer, sheet_name=f"{nome.capitalize()}", index=False)

            worksheet = writer.sheets[f"{nome.capitalize()}"]

            # Ajusta largura automática
            for i, col in enumerate(df.columns):
                # Pega o tamanho máximo entre nome da coluna e valores
                max_len = (
                    max(df[col].astype(str).map(len).max(), len(col)) + 2  # type: ignore
                )  # margem extra
                worksheet.set_column(i, i, max_len)
    elif formato.startswith("pdf"):
        linhas = df.to_dict(orient="records")  # type: ignore
        if agrupados:
            linhas = sorted(
                linhas,
                key=lambda x: tuple(x[col] for col in agrupados),
            )
            grupos = []
            for chave, grupo_iter in groupby(
                linhas, key=lambda x: tuple(x[col] for col in agrupados)
            ):
                grupo_list = list(grupo_iter)
                grupos.append(
                    {
                        "chave": chave,
                        "linhas": grupo_list,
                        "totais": somar_coluna(grupo_list, colunas),
                    }
                )
        else:
            grupos = [
                {"chave": [], "linhas": linhas, "totais": somar_coluna(linhas, colunas)}
            ]
        for linha in linhas:
            for k, v in linha.items():
                try:
                    v = datetime.strptime(v, "%Y-%m-%d")
                except:
                    pass
                if isinstance(v, (datetime, date)):
                    linha[k] = v.strftime("%d/%m/%Y")

        if formato.endswith("v"):
            orientacao = "portrait"
        elif formato.endswith("h"):
            orientacao = "landscape"

        html_string = render_to_string(
            "relatorios/relatorio_exportacao.html",
            {
                "titulo": f"{nome.capitalize()}",
                "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "filtros": filtros,
                "parametros": filtros_atuais,
                "grupos": grupos,
                "colunas": colunas,
                "orientacao": orientacao,  # type: ignore
            },
        )

        html_string = html_string.replace("None", "")

        html = HTML(string=html_string)
        response = HttpResponse(content_type="aplication/pdf")
        response["Content-Disposition"] = (
            f"attachment; filename={nome.capitalize()}.pdf"
        )

        html.write_pdf(response)

    else:
        return HttpResponse(status=400)

    return response


@login_required
def sugestao_view(request):
    if request.method == "POST":
        form = SugestaoForm(request.POST)
        if form.is_valid():
            user = request.user
            perfil = get_object_or_404(Perfil, user=user.id)
            assunto = form.cleaned_data["assunto"]
            mensagem = form.cleaned_data["mensagem"]

            send_mail(
                assunto,
                mensagem + "\n" + user.email,
                "topbanho@postotrevo.com.br",
                ["jucinei6+o5jgzoi86c8ydffpexpk@boards.trello.com"],
                fail_silently=True,
            )

            return redirect("home_view")
    else:
        form = SugestaoForm()

    return render(request, "sugestao.html", {"form": form})


@login_required
def agendar_emissao(request, relatorio_id):
    relatorio = Relatorios.objects.get(id=relatorio_id)  # type: ignore

    if request.method == "POST":
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = AgendamentoForm()

    return render(request, "agendamento.html", {"form": form, "relatorio": relatorio})
