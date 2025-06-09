# forms.py
from django import forms
from django.forms import modelformset_factory
from .models import Empresa, Filtros, Relatorios, Setores, Perfil

FILTER_TYPES = [
    ("data", "Data"),
    ("decimal", "Decimal"),
    ("texto", "Texto"),
    ("inteiro", "Inteiro"),
    ("empresa", "Empresa"),
]


# cadastrar_usuario
class CadastroUsuarioForm(forms.ModelForm):
    nome = forms.CharField(widget=forms.TextInput, label="Nome")
    usuario = forms.CharField(widget=forms.TextInput, label="Usuário")
    email = forms.EmailField(widget=forms.EmailInput, label="Email")
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput, label="Confirmar Senha"
    )
    is_superuser = forms.BooleanField(label="É administrador?", required=False)
    relatorios_permitidos = forms.ModelMultipleChoiceField(
        queryset=Relatorios.objects.all(),  # type: ignore
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Relatórios Permitidos",
    )
    setores = forms.ModelMultipleChoiceField(
        queryset=Setores.objects.all(),  # type: ignore
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Setor permitido",
    )

    class Meta:
        model = Perfil
        fields = ["user", "is_superuser"]

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar = cleaned_data.get("confirmar_senha")

        if senha and confirmar and senha != confirmar:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data


# editar_usuario
class EditarUsuarioForm(forms.Form):
    nome = forms.CharField(widget=forms.TextInput, label="Nome")
    usuario = forms.CharField(widget=forms.TextInput, label="Usuário")
    email = forms.EmailField(widget=forms.EmailInput, label="Email")
    is_superuser = forms.BooleanField(required=False, label="Admin")
    relatorios = forms.ModelMultipleChoiceField(
        queryset=Relatorios.objects.all(),  # type: ignore
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Relatórios permitidos",
    )
    setores = forms.ModelMultipleChoiceField(
        queryset=Setores.objects.all(),  # type: ignore
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Setores",
    )


# alterar_senha
class AlterarSenhaForm(forms.Form):
    nova_senha = forms.CharField(widget=forms.PasswordInput, label="Nova Senha")
    confirmar = forms.CharField(
        widget=forms.PasswordInput, label="Confirmar Nova Senha"
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("nova_senha") != cleaned.get("confirmar"):
            raise forms.ValidationError("As senhas não coincidem.")
        return cleaned


# cadastrar_relatorio
class RelatorioForm(forms.ModelForm):
    class Meta:
        model = Relatorios
        fields = ["nome", "query", "setores"]


# cadastrar_filtro
class FiltroInlineForm(forms.ModelForm):
    class Meta:
        model = Filtros
        fields = ["exibicao", "variavel", "tipo"]


FiltroForm = modelformset_factory(Filtros, form=FiltroInlineForm, can_delete=True)


# cadastrar_setor
class SetorForm(forms.ModelForm):
    class Meta:
        model = Setores
        fields = ["nome"]


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["codigo_interno", "nome"]
