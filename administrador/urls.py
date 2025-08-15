from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    admin_view,
    alterar_senha_usuario,
    cadastrar_relatorio,
    editar_relatorios,
    cadastrar_usuario,
    deletar_usuario,
    editar_usuario,
    excluir_relatorio,
    visualizar_logs,
    criar_setor,
    excluir_setor,
    criar_empresa,
    excluir_empresa,
    adicionar_filtros,
    confirmar_adicao_filtros,
)

urlpatterns = [
    path("", admin_view, name="admin_view"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("usuarios/cadastrar/", cadastrar_usuario, name="cadastrar_usuario"),
    path("usuarios/<int:user_id>/editar/", editar_usuario, name="editar_usuario"),
    path(
        "usuarios/<int:user_id>/senha/",
        alterar_senha_usuario,
        name="alterar_senha_usuario",
    ),
    path("usuarios/<int:user_id>/deletar/", deletar_usuario, name="deletar_usuario"),
    path("relatorios/cadastrar/", cadastrar_relatorio, name="cadastrar_relatorio"),
    path(
        "relatorios/configurar/<int:relatorio_id>/",
        editar_relatorios,
        name="editar_relatorios",
    ),
    path(
        "relatorios/excluir/<int:relatorio_id>/",
        excluir_relatorio,
        name="excluir_relatorio",
    ),
    path("setores/cadastrar/", criar_setor, name="criar_setor"),
    path("setores/excluir/<int:setor_id>/", excluir_setor, name="excluir_setor"),
    path("logs/", visualizar_logs, name="visualizar_logs"),
    path("empresa/cadastrar/", criar_empresa, name="criar_empresa"),
    path("empresa/excluir/<int:empresa_id>/", excluir_empresa, name="excluir_empresa"),
    path('relatorios/<int:relatorio_id>/confirmar/', confirmar_adicao_filtros, name='confirmar_adicao_filtros'),
    path('relatorios/<int:relatorio_id>/filtros/<int:quantidade>/', adicionar_filtros, name='adicionar_filtros'),
]
