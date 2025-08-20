from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from administrador.models import Relatorios, Filtros, Perfil, Setores, Empresa
from gerador_relatorios.utils import executar_query
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import datetime
import pandas as pd

# Create your views here.


@login_required
def home_view(request):
    user = request.user
    perfil = get_object_or_404(Perfil, user=user.id)
    setores_usuario = perfil.setor.all()

    setor_nome = request.GET.get("setor")
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
    elif setor_nome:
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
        try:
            for data in resultados.select_dtypes(include="datetime64[ns]").columns:
                resultados[data] = resultados[data].dt.strftime("%Y-%m-%d")
        except:
            pass
        request.session["relatorio_gerado"] = resultados.to_json(date_format="iso")
        request.session["relatorio_nome"] = relatorio.nome
        request.session["filtros"] = filtros
        request.session["filtros_gerados"] = parametros
    context = {
        "relatorio": relatorio,
        "filtros": filtros,  # Envia os filtros usados de volta para o template
        "resultados": resultados.to_html(index=False, classes="table table-striped table-dark text-light table-bordered border-white rounded").replace("None","").replace("NaN",""),  # type: ignore
    }

    return render(request, "relatorios/gerar.html", context)


def download_manager(request, formato):
    df_json = request.session.get("relatorio_gerado")
    nome = request.session.get("relatorio_nome")
    filtros = request.session.get("filtros")
    filtros_atuais = request.session.get("filtros_gerados")
    for x, y in filtros_atuais.items():
        try:
            y = datetime.strptime(y, '%Y-%m-%d')
            print(y)
        except:
            print(y)
    
    if not df_json:
        return HttpResponse(status=404)

    df = pd.read_json(df_json)
    for data in df.select_dtypes(include="datetime64[ns]").columns:
        df[data] = df[data].dt.strftime("%Y-%m-%d")

    if formato == "csv":
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
                    max(df[col].astype(str).map(len).max(), len(col)) + 2
                )  # margem extra
                worksheet.set_column(i, i, max_len)
    elif formato == "pdfv":
        tabela_html = df.to_html(
            index=False, border=0, classes="tabela", justify="left"
        )

        html_string = render_to_string(
            "relatorios/relatorio_exportacao.html",
            {
                "titulo": f"{nome.capitalize()}",
                "data_geracao": datetime.now().strftime("%D/%M/%Y %H:%M"),
                "filtros": filtros,
                "parametros": filtros_atuais,
                "tabela_html": tabela_html.replace("None", "").replace("NaN", ""),
                "orientacao": "portrait",
            },
        )

        html = HTML(string=html_string)
        response = HttpResponse(content_type="aplication/pdf")
        response["Content-Disposition"] = (
            f"attachment; filename={nome.capitalize()}.pdf"
        )
        html.write_pdf(response)
    elif formato == "pdfh":
        tabela_html = df.to_html(
            index=False, border=0, classes="tabela", justify="left"
        )

        html_string = render_to_string(
            "relatorios/relatorio_exportacao.html",
            {
                "titulo": f"{nome.capitalize()}",
                "data_geracao": datetime.now().strftime("%D/%M/%Y %H:%M"),
                "filtros": filtros,
                "parametros": filtros_atuais,
                "tabela_html": tabela_html.replace("None", "").replace("NaN", ""),
                "orientacao": "landscape",
            },
        )

        html = HTML(string=html_string)
        response = HttpResponse(content_type="aplication/pdf")
        response["Content-Disposition"] = (
            f"attachment; filename={nome.capitalize()}.pdf"
        )
        html.write_pdf(response)

    else:
        return HttpResponse(status=400)

    return response
