from django.shortcuts import render, get_object_or_404
from administrador.models import Relatorios, Filtros, Perfil, Setores
from gerador_relatorios.utils import executar_query
from django.contrib.auth.decorators import login_required

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

    if relatorio_id:
        # Mostrar filtros do relatório
        relatorio = get_object_or_404(Relatorios, id=relatorio_id)
        filtros = Filtros.objects.filter(relatorio=relatorio.id)  # type: ignore

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
    }
    print(context)
    return render(request, "home.html", context)


def gerar_relatorio(request, relatorio_id):
    relatorio = get_object_or_404(Relatorios, id=relatorio_id)
    filtro = Filtros.objects.filter(relatorio_id=relatorio_id)

    # Inicializa variáveis
    resultados = []
    filtros_request = {}
    
    if request.method == "POST":
        # Extrai filtros do request.POST (ajuste conforme seus campos)
        filtros_request = filtro
        
        # Debug: imprima os filtros recebidos
        print("Filtros recebidos:", filtros_request)
        
        try:
            resultados = executar_query(relatorio, filtros_request, using='banco_remoto')
            # Debug: imprima os resultados obtidos
            print("Resultados da query:", resultados)
        except Exception as e:
            print("Erro ao executar query:", str(e))
            # Você pode adicionar uma mensagem de erro ao contexto

    context = {
        "relatorio": relatorio,
        "filtros": filtros_request,  # Envia os filtros usados de volta para o template
        "resultados": resultados,
    }

    return render(request, "relatorios/gerar.html", context)
