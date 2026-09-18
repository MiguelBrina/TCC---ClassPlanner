from django import forms

from .models import Disciplina, Tema, Conteudo, Aluno, Matricula, Aula, DiarioDeBordo, Registro, Pagamento

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ["nome"]

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
        fields = ["aluno", "disciplina", "data_inicio"]
        widgets = {
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
        }



class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ["aluno", "disciplina", "data", "horario"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "horario": forms.TimeInput(attrs={"type": "time"}),
        }



class DiarioDeBordoForm(forms.ModelForm):
    class Meta:
        model = DiarioDeBordo
        fields = ["matricula"]


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ["diario", "data", "observacao", "temas", "conteudos"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "observacao": forms.Textarea(attrs={"rows": 3}),
        }

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ["aluno", "mes", "pago"]
        widgets = {
            "mes": forms.DateInput(attrs={"type": "date"}),
        }
