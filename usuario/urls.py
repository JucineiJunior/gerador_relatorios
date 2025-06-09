from django.urls import path

from .views import home_view, gerar_relatorio

urlpatterns = [
    path("", home_view, name="home_view"),
    path("gerar/<int:relatorio_id>/", gerar_relatorio, name="gerar_relatorio"),
]
