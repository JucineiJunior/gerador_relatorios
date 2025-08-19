from django.urls import path
from django.shortcuts import redirect

from .views import home_view, gerar_relatorio, download_manager, sugestao_view

urlpatterns = [
    path("", home_view, name="home_view"),
    path("gerar/<int:relatorio_id>/", gerar_relatorio, name="gerar_relatorio"),
    path(
        "gerar/<int:relatorio_id>/admin",
        lambda request, relatorio_id: redirect("/admin/"),
        name="admin_redirect",
    ),
    path("download/<str:formato>/", download_manager, name="exports"),
    path("contato", sugestao_view, name="contato")
]
