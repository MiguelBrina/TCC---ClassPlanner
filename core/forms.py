import re

from django import forms

from .models import (
    Aluno,
    Aula,
    Conteudo,
    DiarioDeBordo,
    Disciplina,
    Matricula,
    Pagamento,
    Registro,
    Tema,
)


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ["nome", "cor"]
        widgets = {
            "cor": forms.TextInput(
                attrs={
                    "type": "color",
                }
            ),
        }

    def clean_cor(self):
        cor = self.cleaned_data["cor"]

        if not re.fullmatch(
            r"#[0-9A-Fa-f]{6}",
            cor,
        ):
            raise forms.ValidationError(
                "Escolha uma cor válida."
            )

        return cor.lower()


class TemaForm(forms.ModelForm):
    class Meta:
        model = Tema
        fields = ["nome"]


class ConteudoForm(forms.ModelForm):
    class Meta:
        model = Conteudo
        fields = ["nome"]


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ["nome_completo", "telefone"]


class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = [
            "aluno",
            "disciplina",
            "data_inicio",
        ]
        widgets = {
            "data_inicio": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }


class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = [
            "aluno",
            "disciplina",
            "data",
            "horario",
        ]
        widgets = {
            "data": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "horario": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),
        }


class DiarioDeBordoForm(forms.ModelForm):
    class Meta:
        model = DiarioDeBordo
        fields = ["matricula"]


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = [
            "diario",
            "data",
            "observacao",
            "temas",
            "conteudos",
        ]
        widgets = {
            "data": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = [
            "aluno",
            "mes",
            "pago",
        ]
        widgets = {
            "mes": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }