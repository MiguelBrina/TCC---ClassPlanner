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

        Professor.objects.get_or_create(
            usuario=user
        )


class ConfiguracaoAgendaForm(forms.Form):

    nome_exibicao = forms.CharField(
        label="Como você quer ser chamado?",
        max_length=100,
        required=False,
    )

    segunda = forms.BooleanField(
        label="Segunda-feira",
        required=False,
    )

    segunda_inicio = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    segunda_fim = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    terca = forms.BooleanField(
        label="Terça-feira",
        required=False,
    )

    terca_inicio = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    terca_fim = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    quarta = forms.BooleanField(
        label="Quarta-feira",
        required=False,
    )

    quarta_inicio = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    quarta_fim = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    quinta = forms.BooleanField(
        label="Quinta-feira",
        required=False,
    )

    quinta_inicio = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    quinta_fim = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    sexta = forms.BooleanField(
        label="Sexta-feira",
        required=False,
    )

    sexta_inicio = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    sexta_fim = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    sabado = forms.BooleanField(
        label="Sábado",
        required=False,
    )

    sabado_inicio = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    sabado_fim = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    domingo = forms.BooleanField(
        label="Domingo",
        required=False,
    )

    domingo_inicio = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    domingo_fim = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
    )

    def clean(self):
        cleaned_data = super().clean()

        dias = [
            "segunda",
            "terca",
            "quarta",
            "quinta",
            "sexta",
            "sabado",
            "domingo",
        ]

        for dia in dias:
            selecionado = cleaned_data.get(dia)

            if selecionado:
                inicio = cleaned_data.get(f"{dia}_inicio")
                fim = cleaned_data.get(f"{dia}_fim")

                if not inicio or not fim:
                    raise forms.ValidationError(
                        f"Informe o horário de início e fim para {dia}."
                    )

                if inicio >= fim:
                    raise forms.ValidationError(
                        f"O horário final de {dia} deve ser depois do horário inicial."
                    )

        return cleaned_data