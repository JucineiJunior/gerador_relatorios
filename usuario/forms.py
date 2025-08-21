from django import forms


class SugestaoForm(forms.Form):
    assunto = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control m-2"}),
    )

    mensagem = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control m-2 ", "rows": 10}),
        required=True,
    )
