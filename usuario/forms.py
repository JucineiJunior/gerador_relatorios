from django import forms

from administrador.models import Perfil
from usuario.models import Agendamentos


class SugestaoForm(forms.Form):
    assunto = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control m-2"}),
    )

    mensagem = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control m-2 ", "rows": 10}),
        required=True,
    )


class AgendamentoForm(forms.ModelForm):
    beneficiados = forms.ModelMultipleChoiceField(
        queryset=Perfil.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Usuarios",
    )
    metodo = forms.ChoiceField(choices=Agendamentos.METODO_CHOICES)
    intervalo = forms.IntegerField()

    class Meta:
        model = Agendamentos
        exclude = ["usuario", "relatorio"]
