from django import forms
import json

from .models import Professor, DisponibilidadeProfessor


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

    dias = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    horarios = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def clean_dias(self):
        valor = self.cleaned_data.get("dias", "")

        if not valor:
            raise forms.ValidationError(
                "Selecione pelo menos um dia da semana."
            )

        try:
            dias = json.loads(valor)
        except json.JSONDecodeError:
            raise forms.ValidationError(
                "Os dias selecionados são inválidos."
            )

        dias_validos = {
            "segunda",
            "terca",
            "quarta",
            "quinta",
            "sexta",
            "sabado",
            "domingo",
        }

        if not isinstance(dias, list):
            raise forms.ValidationError(
                "Os dias selecionados são inválidos."
            )

        if not dias:
            raise forms.ValidationError(
                "Selecione pelo menos um dia da semana."
            )

        if not all(dia in dias_validos for dia in dias):
            raise forms.ValidationError(
                "Um dos dias selecionados é inválido."
            )

        return dias

    def clean_horarios(self):
        valor = self.cleaned_data.get("horarios", "")

        if not valor:
            raise forms.ValidationError(
                "Adicione pelo menos um horário."
            )

        try:
            horarios = json.loads(valor)
        except json.JSONDecodeError:
            raise forms.ValidationError(
                "Os horários informados são inválidos."
            )

        if not isinstance(horarios, list) or not horarios:
            raise forms.ValidationError(
                "Adicione pelo menos um horário."
            )

        horarios_validos = []

        for horario in horarios:
            if not isinstance(horario, dict):
                raise forms.ValidationError(
                    "Formato de horário inválido."
                )

            valor_horario = horario.get("horario")

            if not valor_horario:
                raise forms.ValidationError(
                    "Todos os horários precisam ser preenchidos."
                )

            horarios_validos.append({
                "horario": valor_horario,
            })

        return horarios_validos


class ConfiguracaoProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ["nome_exibicao"]
        labels = {
            "nome_exibicao": "Nome de exibição",
        }


class DisponibilidadeForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadeProfessor
        fields = ["dia_semana", "horario"]
        labels = {
            "dia_semana": "Dia da semana",
            "horario": "Horário",
        }


class ExclusaoContaForm(forms.Form):
    nome_exibicao = forms.CharField(
        label="Digite seu nome de exibição para confirmar"
    )

    def __init__(self, *args, professor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.professor = professor

    def clean_nome_exibicao(self):
        nome = self.cleaned_data["nome_exibicao"]

        if nome != self.professor.nome_exibicao:
            raise forms.ValidationError(
                "O nome informado não corresponde ao seu nome de exibição."
            )

        return nome