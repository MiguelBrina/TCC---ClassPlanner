from django import forms

from .models import Professor


class FormularioCadastro(forms.Form):
    nome = forms.CharField(
        label="Nome completo",
        max_length=150,
    )

    def signup(self, request, user):
        user.first_name = self.cleaned_data["nome"]
        user.save()

        Professor.objects.create(
            usuario=user
        )