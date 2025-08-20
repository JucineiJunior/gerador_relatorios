from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.forms import modelformset_factory

from .forms import (
    AlterarSenhaForm,
    CadastroUsuarioForm,
    EditarUsuarioForm,
    FiltroForm,
    RelatorioForm,
    SetorForm,
    EmpresaForm,
    EditarRelatorioForm,
)
from .models import Filtros, Logs, Relatorios, Setores, Perfil, Empresa
from gerador_relatorios.utils import registrar_log


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


# Create your views here.


# admin_view
@login_required
@user_passes_test(is_superuser)
def admin_view(request):
    secao = request.GET.get("secao", "")

    context = {"secao": secao}

    if secao == "relatorios":
        context["relatorios"] = Relatorios.objects.all()  # type: ignore
    elif secao == "logs":
        context["logs"] = Logs.objects.all()  # type: ignore
    elif secao == "setores":
        context["setores"] = Setores.objects.all()  # type: ignore
    elif secao == "usuarios":
        context["usuarios"] = (
            Perfil.objects.select_related("user").prefetch_related("setor").all()  # type: ignore
        )
    elif secao == "empresa":
        context["empresa"] = Empresa.objects.all()  # type: ignore

    return render(request, "admin.html", context)


# criar_usuario
@user_passes_test(is_superuser)
@login_required
def cadastrar_usuario(request):
    if request.method == "POST":
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            # Cria o usuário
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["senha"])
            user.save()

            # Cria o perfil vinculado
            perfil = Perfil.objects.create(  # type: ignore
                user=user, nome=form.cleaned_data["nome"]
            )
            perfil.relatorios.set(form.cleaned_data["relatorios_permitidos"])
            perfil.setor.set(form.cleaned_data["setores"])
            perfil.save()

            registrar_log(perfil, f"Cadastrou o usuário {perfil.user}")
            messages.success(request, "Usuário cadastrado com sucesso!")
            return redirect("/admin/?secao=usuarios")
        else:
            print(form)
    else:
        form = CadastroUsuarioForm()

    return render(request, "usuarios/cadastrar.html", {"form": form})


# editar_usuario
@user_passes_test(is_superuser)
@login_required
def editar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    perfil, _ = Perfil.objects.get_or_create(user=user)  # type: ignore

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST)
        if form.is_valid():
            user.is_superuser = form.cleaned_data["is_superuser"]
            user.email = form.cleaned_data["email"]
            user.save()

            perfil.nome = form.cleaned_data["nome"]
            perfil.relatorios.set(form.cleaned_data["relatorios"])
            perfil.setor.set(form.cleaned_data["setores"])
            perfil.save()

            registrar_log(perfil, f"editou o usuario {perfil.nome}")

            messages.success(request, "Usuário atualizado com sucesso!")
            return redirect("/admin/?secao=usuarios")
        print(form.is_valid())
    else:
        form = EditarUsuarioForm(
            initial={
                "nome": perfil.nome,
                "email": user.email,
                "is_superuser": user.is_superuser,
                "relatorios": perfil.relatorios.all(),
                "setores": perfil.setor.all(),
            },
        )

    return render(
        request,
        "usuarios/editar.html",
        {"form": form, "usuario": user, "perfil": perfil},
    )


# alterar_senha
@user_passes_test(is_superuser)  # type: ignore
@login_required  # type: ignore
def alterar_senha_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    usuario, _ = Perfil.objects.get_or_create(user=user)  # type: ignore

    if request.method == "POST":
        form = AlterarSenhaForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["nova_senha"])
            user.save()
            perfil = Perfil.objects.get(id=request.user.id)  # type: ignore
            registrar_log(perfil, f"Alterou a senha do usuário {user.username}")
            messages.success(request, "Senha atualizada com sucesso!")
            return redirect("/admin/?secao=usuarios")
        else:
            return "Erro"
    else:
        form = AlterarSenhaForm()

    return render(
        request, "usuarios/alterar_senha.html", {"form": form, "usuario": usuario}
    )


# deletar_usuario
@user_passes_test(is_superuser)
@login_required
def deletar_usuario(request, user_id):
    usuario = User.objects.get(id=user_id)  # type: ignore

    if request.method == "POST":
        perfil = Perfil.objects.get(id=request.user.id)  # type: ignore
        registrar_log(perfil, f"Excluiu o usuário {usuario.username}")
        usuario.delete()
        messages.success(request, "Usuário excluído com sucesso!")
        return redirect("/admin/?secao=Perfil")

    return render(request, "usuarios/deletar.html", {"usuario": usuario})


# criar_relatorio
@user_passes_test(is_superuser)
@login_required
def cadastrar_relatorio(request):
    if request.method == "POST":
        form = RelatorioForm(request.POST)
        if form.is_valid():
            relatorio = form.save()
            return redirect("confirmar_adicao_filtros", relatorio_id=relatorio.id)
    else:
        form = RelatorioForm()
    return render(request, "relatorios/cadastrar.html", {"form": form})


def confirmar_adicao_filtros(request, relatorio_id):
    if request.method == "POST":
        deseja_filtros = request.POST.get("deseja_filtros")
        try:
            quantidade = int(request.POST.get("quantidade", 0))
        except TypeError:
            quantidade = 0
        if deseja_filtros == "sim" and quantidade > 0:
            return redirect(
                "adicionar_filtros", relatorio_id=relatorio_id, quantidade=quantidade
            )
        else:
            return redirect("/admin/?secao=relatorios")  # Ou outra página final

    return render(request, "filtros/confirmar.html", {"relatorio_id": relatorio_id})


def adicionar_filtros(request, relatorio_id, quantidade=0):
    relatorio = get_object_or_404(Relatorios, id=relatorio_id)
    FiltroFormSet = modelformset_factory(
        Filtros, form=FiltroForm, extra=int(quantidade)
    )

    if request.method == "POST":
        formset = FiltroFormSet(request.POST, queryset=Filtros.objects.none())  # type: ignore
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    filtro = form.save(commit=False)
                    filtro.relatorio = relatorio
                    filtro.save()
            return redirect("/admin/?secao=relatorios")
    else:
        formset = FiltroFormSet(queryset=Filtros.objects.none())  # type: ignore

    return render(
        request, "filtros/adicionar.html", {"relatorio": relatorio, "formset": formset}
    )


# editar_relatorio
@user_passes_test(is_superuser)
@login_required
def editar_relatorios(request, relatorio_id):
    relatorio = get_object_or_404(Relatorios, id=relatorio_id)

    if request.method == "POST":
        form = EditarRelatorioForm(request.POST)
        if form.is_valid():
            relatorio.nome = form.cleaned_data["nome"]
            relatorio.query = form.cleaned_data["query"]
            relatorio.setores = form.cleaned_data["setor"]
            relatorio.save()

            messages.success(request, "Relatorio atualizado com sucesso")

            return redirect("/admin/?secao=relatorios")
        print(form.cleaned_data)
    else:
        form = EditarRelatorioForm(
            initial={
                "nome": relatorio.nome,
                "query": relatorio.query,
                "setor": relatorio.setores,
            }
        )

    return render(
        request,
        "relatorios/configurar.html",
        {"form": form, "relatorio": relatorio},
    )


# deletar_relatorio
@user_passes_test(is_superuser)
@login_required
def excluir_relatorio(request, relatorio_id):
    relatorio = get_object_or_404(Relatorios, id=relatorio_id)
    if request.method == "POST":
        perfil = Perfil.objects.get(id=request.user.id)  # type: ignore
        registrar_log(perfil, f"Excluiu o relatório '{relatorio.nome}'")
        relatorio = Relatorios.objects.get(id=relatorio_id).delete()[1]  # type: ignore
        messages.success(request, "Relatório excluído com sucesso!")
        return redirect("/admin/?secao=relatorios")
    return render(request, "relatorios/excluir.html", {"relatorio": relatorio})


# criar_setor
@user_passes_test(is_superuser)
@login_required
def criar_setor(request):
    if request.method == "POST":
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            registrar_log(
                Perfil.objects.get(id=request.user.id),  # type: ignore
                f"Criou um setor {form.save()}",
            )
            messages.success(request, "Setor criado com sucesso!")
            return redirect("/admin/?secao=setores")
    else:
        form = SetorForm()
    return render(request, "setores/criar.html", {"form": form})


# deletar_setor
@user_passes_test(is_superuser)
@login_required
def excluir_setor(request, setor_id):
    setor = get_object_or_404(Setores, id=setor_id)
    if request.method == "POST":
        setor.delete()
        messages.success(request, "Setor excluído com sucesso!")
        return redirect("/admin/?secao=setores")
    return render(request, "setores/excluir.html", {"setor": setor})


# vizualizar_logs
@user_passes_test(is_superuser)
@login_required
def visualizar_logs(request):
    logs = Logs.objects.all().order_by("data").desc()  # type: ignore

    # filtros opcionais
    usuario = request.GET.get("usuario")
    if usuario != "":
        logs = logs.filter(usuario__username__icontains=usuario)

    acao = request.GET.get("acao")
    if acao != "":
        logs = logs.filter(acao__icontains=acao)

    return render(request, "admin/logs.html", {"secao": "logs", "logs": logs})


# criar_empresa
@user_passes_test(is_superuser)
@login_required
def criar_empresa(request):
    if request.method == "POST":
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            registrar_log(
                Perfil.objects.get(id=request.user.id),  # type: ignore
                f"Cadastrou empresa {form.save}",
            )
            messages.success(request, "Empresa criada com sucesso!")
            return redirect("/admin/?secao=empresa")
    else:
        form = EmpresaForm()
    return render(request, "empresa/criar.html", {"form": form})


# deletar_empresa
@user_passes_test(is_superuser)
@login_required
def excluir_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    if request.method == "POST":
        empresa.delete()
        messages.success(request, "Empresa excluído com sucesso!")
        return redirect("/admin/?secao=empresa")
    return render(request, "empresa/excluir.html", {"empresa": empresa})
