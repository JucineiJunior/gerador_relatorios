from django import forms


class SugestaoForm(forms.Form):
    mensagem = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control ", "rows": 10}),
        required=True,
    )
    assunto = forms.ChoiceField(
        widget=forms.Select, choices=[(0, "Sugestão"), (1, "Solicitação")]
    )
