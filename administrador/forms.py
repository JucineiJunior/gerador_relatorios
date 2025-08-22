# forms.py
from django import forms

from administrador.models import Colunas, Empresa, Filtros, Relatorios, Setores, User

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
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput, label="Confirmar Senha"
    )
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
        model = User
        fields = ["username", "email", "is_superuser"]

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")
        if senha != confirmar_senha:
            self.add_error("confirmar_senha", "As senhas não conferem.")
        return cleaned_data


# editar_usuario
class EditarUsuarioForm(forms.Form):
    nome = forms.CharField(widget=forms.TextInput, label="Nome")
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
    confirmar = forms.CharField(widget=forms.PasswordInput, label="Confirmar Senha")

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


class EditarRelatorioForm(forms.Form):
    nome = forms.CharField(widget=forms.TextInput, label="Nome")
    query = forms.CharField(widget=forms.Textarea, label="query")
    setor = forms.ModelChoiceField(
        queryset=Setores.objects.all(), required=True, label="setores"
    )


class FiltroForm(forms.ModelForm):
    class Meta:
        model = Filtros
        fields = ["exibicao", "variavel", "tipo"]


class ColunasForm(forms.ModelForm):
    class Meta:
        model = Colunas
        fields = ["coluna", "relatorio_id"]


# cadastrar_setor
class SetorForm(forms.ModelForm):
    class Meta:
        model = Setores
        fields = ["nome"]


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["codigo_interno", "nome"]
