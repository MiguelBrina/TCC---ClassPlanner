
import re
from decimal import Decimal

from django import forms
from django.utils import timezone

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


class ConteudoCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def create_option(
        self, name, value, label, selected, index,
        subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index,
            subindex=subindex, attrs=attrs
        )

        if value:
            conteudo = value.instance

            if conteudo:
                option["attrs"]["data-tema-id"] = str(
                    conteudo.tema_id
                )

        return option


# ============================================================
# 1. FORMULÁRIO DE DISCIPLINA
# ============================================================

class DisciplinaForm(forms.ModelForm):

    class Meta:
        model = Disciplina
        fields = ["nome", "cor"]

        widgets = {
            "cor": forms.TextInput(
                attrs={"type": "color"}
            ),
        }

    def clean_cor(self):
        cor = self.cleaned_data["cor"]

        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", cor):
            raise forms.ValidationError(
                "Escolha uma cor válida."
            )

        return cor.lower()


# ============================================================
# 2. FORMULÁRIO DE TEMA
# ============================================================

class TemaForm(forms.ModelForm):

    class Meta:
        model = Tema
        fields = ["nome"]


# ============================================================
# 3. FORMULÁRIO DE CONTEÚDO
# ============================================================

class ConteudoForm(forms.ModelForm):

    class Meta:
        model = Conteudo
        fields = ["nome"]


# ============================================================
# 4. FORMULÁRIO DE ALUNO
# ============================================================

class AlunoForm(forms.ModelForm):

    class Meta:
        model = Aluno
        fields = ["nome_completo", "telefone"]

    def clean_telefone(self):
        telefone = self.cleaned_data["telefone"]

        numeros = re.sub(r"\D", "", telefone)

        if len(numeros) not in [10, 11]:
            raise forms.ValidationError(
                "Informe um telefone válido com DDD."
            )

        ddd = numeros[:2]
        numero = numeros[2:]

        if len(numero) == 9:
            return f"({ddd}) {numero[:5]}-{numero[5:]}"

        return f"({ddd}) {numero[:4]}-{numero[4:]}"


# ============================================================
# 5. FORMULÁRIO DE MATRÍCULA INDIVIDUAL
# ============================================================

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
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, professor, **kwargs):
        super().__init__(*args, **kwargs)

        self.professor = professor

        self.fields["aluno"].queryset = (
            Aluno.objects
            .filter(professor=professor)
            .order_by("nome_completo")
        )

        self.fields["disciplina"].queryset = (
            Disciplina.objects
            .filter(professor=professor)
            .order_by("nome")
        )

    def clean(self):
        dados = super().clean()

        aluno = dados.get("aluno")
        disciplina = dados.get("disciplina")

        if aluno and disciplina:

            if aluno.professor_id != self.professor.pk:
                self.add_error(
                    "aluno",
                    "Este aluno não pertence à sua conta.",
                )

            if disciplina.professor_id != self.professor.pk:
                self.add_error(
                    "disciplina",
                    "Esta disciplina não pertence à sua conta.",
                )

            matriculas_existentes = Matricula.objects.filter(
                aluno=aluno,
                disciplina=disciplina,
            )

            if self.instance.pk:
                matriculas_existentes = (
                    matriculas_existentes.exclude(
                        pk=self.instance.pk
                    )
                )

            if matriculas_existentes.exists():
                self.add_error(
                    "disciplina",
                    "Este aluno já está matriculado nesta disciplina.",
                )

        return dados


# ============================================================
# 6. FORMULÁRIO DE MATRÍCULA MÚLTIPLA
# ============================================================

class MatricularDisciplinasForm(forms.Form):

    disciplinas = forms.ModelMultipleChoiceField(
        queryset=Disciplina.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label="Disciplinas",
    )

    valor_mensal = forms.DecimalField(
        required=True,
        min_value=Decimal("0.01"),
        max_digits=10,
        decimal_places=2,
        label="Mensalidade padrão por disciplina (R$)",
        widget=forms.NumberInput(
            attrs={
                "step": "0.01",
                "min": "0.01",
                "placeholder": "Ex.: 150,00",
            }
        ),
        help_text=(
            "Esse valor será usado nas próximas mensalidades. "
            "Você poderá alterar o valor de um mês específico "
            "no financeiro."
        ),
    )

    data_inicio = forms.DateField(
        required=True,
        initial=timezone.localdate,
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
        label="Data de início",
    )

    def __init__(self, *args, professor, aluno, **kwargs):
        super().__init__(*args, **kwargs)

        self.professor = professor
        self.aluno = aluno

        self.aluno_autorizado = (
            aluno.professor_id == professor.pk
        )

        if self.aluno_autorizado:
            disciplinas_matriculadas = (
                aluno.matriculas.values_list(
                    "disciplina_id",
                    flat=True,
                )
            )

            disciplinas_permitidas = (
                Disciplina.objects
                .filter(professor=professor)
                .exclude(pk__in=disciplinas_matriculadas)
                .order_by("nome")
            )
        else:
            disciplinas_permitidas = Disciplina.objects.none()

        self.fields["disciplinas"].queryset = (
            disciplinas_permitidas
        )

    def clean(self):
        dados = super().clean()

        if not self.aluno_autorizado:
            raise forms.ValidationError(
                "Não é permitido matricular disciplinas para este aluno."
            )

        return dados


# ============================================================
# 7. FORMULÁRIO DE AULA
# ============================================================

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
                attrs={"type": "date"}
            ),
            "horario": forms.TimeInput(
                attrs={"type": "time"}
            ),
        }

    def __init__(self, *args, professor, **kwargs):
        super().__init__(*args, **kwargs)

        self.professor = professor

        self.fields["aluno"].queryset = (
            Aluno.objects
            .filter(professor=professor)
            .order_by("nome_completo")
        )

        self.fields["disciplina"].queryset = (
            Disciplina.objects
            .filter(professor=professor)
            .order_by("nome")
        )

    def clean(self):
        dados = super().clean()

        aluno = dados.get("aluno")
        disciplina = dados.get("disciplina")

        if aluno and aluno.professor_id != self.professor.pk:
            self.add_error(
                "aluno",
                "Este aluno não pertence à sua conta.",
            )

        if (
            disciplina
            and disciplina.professor_id != self.professor.pk
        ):
            self.add_error(
                "disciplina",
                "Esta disciplina não pertence à sua conta.",
            )

        return dados


# ============================================================
# 8. FORMULÁRIO DE CRIAÇÃO DE DIÁRIO DE BORDO
# ============================================================

class DiarioDeBordoForm(forms.ModelForm):

    class Meta:
        model = DiarioDeBordo
        fields = ["matricula"]

    def __init__(self, *args, professor, **kwargs):
        super().__init__(*args, **kwargs)

        self.professor = professor

        matriculas_permitidas = (
            Matricula.objects
            .filter(
                aluno__professor=professor,
                disciplina__professor=professor,
            )
            .select_related("aluno", "disciplina")
        )

        matriculas_permitidas = (
            matriculas_permitidas
            .filter(diario__isnull=True)
            .order_by("aluno__nome_completo", "disciplina__nome")
        )

        self.fields["matricula"].queryset = (
            matriculas_permitidas
        )


# ============================================================
# 9. FORMULÁRIO GENÉRICO DE REGISTRO
# ============================================================

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
                attrs={"type": "date"}
            ),
            "observacao": forms.Textarea(
                attrs={"rows": 3}
            ),
            "temas": forms.CheckboxSelectMultiple(),
            "conteudos": forms.CheckboxSelectMultiple(),
        }

    def __init__(
        self,
        *args,
        professor,
        diario=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.professor = professor

        instancia = kwargs.get("instance")

        if diario is None and instancia and instancia.pk:
            diario = instancia.diario

        self.diario_contexto = diario

        diarios_permitidos = (
            DiarioDeBordo.objects
            .filter(
                matricula__aluno__professor=professor,
                matricula__disciplina__professor=professor,
            )
            .select_related(
                "matricula",
                "matricula__aluno",
                "matricula__disciplina",
            )
        )

        temas_permitidos = Tema.objects.filter(
            disciplina__professor=professor,
        ).order_by("nome")

        conteudos_permitidos = Conteudo.objects.filter(
            tema__disciplina__professor=professor,
        ).order_by("nome")

        if diario is not None:

            diario_autorizado = (
                diario.matricula.aluno.professor_id == professor.pk
                and diario.matricula.disciplina.professor_id
                == professor.pk
            )

            if diario_autorizado:

                diarios_permitidos = diarios_permitidos.filter(
                    pk=diario.pk,
                )

                disciplina = diario.matricula.disciplina

                temas_permitidos = temas_permitidos.filter(
                    disciplina=disciplina,
                )

                conteudos_permitidos = (
                    conteudos_permitidos.filter(
                        tema__disciplina=disciplina,
                    )
                )
            else:
                diarios_permitidos = (
                    DiarioDeBordo.objects.none()
                )
                temas_permitidos = Tema.objects.none()
                conteudos_permitidos = Conteudo.objects.none()

        self.fields["diario"].queryset = diarios_permitidos
        self.fields["temas"].queryset = temas_permitidos
        self.fields["conteudos"].queryset = (
            conteudos_permitidos
        )

    def clean(self):
        dados = super().clean()

        diario = dados.get("diario")
        temas = dados.get("temas")
        conteudos = dados.get("conteudos")

        if diario:
            disciplina_id = (
                diario.matricula.disciplina_id
            )

            if temas:
                if any(
                    tema.disciplina_id != disciplina_id
                    for tema in temas
                ):
                    self.add_error(
                        "temas",
                        "Selecione somente temas desta disciplina.",
                    )

            if conteudos:
                if any(
                    conteudo.tema.disciplina_id != disciplina_id
                    for conteudo in conteudos
                ):
                    self.add_error(
                        "conteudos",
                        "Selecione somente conteúdos desta disciplina.",
                    )

        return dados


# ============================================================
# 10. FORMULÁRIO DE REGISTRO ASSOCIADO A UMA MATRÍCULA
# ============================================================

class RegistroMatriculaForm(forms.ModelForm):

    data = forms.DateField(
        required=True,
        initial=timezone.localdate,
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
        label="Data do registro",
    )

    class Meta:
        model = Registro

        fields = [
            "data",
            "observacao",
            "temas",
            "conteudos",
        ]

        widgets = {
            "observacao": forms.Textarea(
                attrs={"rows": 3}
            ),
            "temas": forms.CheckboxSelectMultiple(),
            "conteudos": ConteudoCheckboxSelectMultiple(),
        }

    def __init__(
        self,
        *args,
        professor,
        disciplina,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.professor = professor
        self.disciplina = disciplina

        self.disciplina_autorizada = (
            disciplina.professor_id == professor.pk
        )

        if self.disciplina_autorizada:

            self.fields["temas"].queryset = (
                Tema.objects
                .filter(
                    disciplina=disciplina,
                )
                .order_by("nome")
            )

            self.fields["conteudos"].queryset = (
                Conteudo.objects
                .filter(
                    tema__disciplina=disciplina,
                )
                .order_by("nome")
            )
        else:

            self.fields["temas"].queryset = (
                Tema.objects.none()
            )

            self.fields["conteudos"].queryset = (
                Conteudo.objects.none()
            )

    def clean(self):
        dados = super().clean()

        if not self.disciplina_autorizada:
            raise forms.ValidationError(
                "Não é permitido registrar informações nesta disciplina."
            )

        temas = dados.get("temas")
        conteudos = dados.get("conteudos")

        if conteudos and not temas:
            self.add_error(
                "temas",
                "Selecione pelo menos um tema para escolher os conteúdos."
            )

        elif temas and conteudos:
            temas_ids = temas.values_list("id", flat=True)

            for conteudo in conteudos:
                if conteudo.tema_id not in temas_ids:
                    self.add_error(
                        "conteudos",
                        "Os conteúdos selecionados devem pertencer aos temas escolhidos."
                    )
                    break

        return dados


# ============================================================
# 11. FORMULÁRIO DE PAGAMENTO ANTIGO
# ============================================================

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
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, professor, **kwargs):
        super().__init__(*args, **kwargs)

        self.professor = professor

        self.fields["aluno"].queryset = (
            Aluno.objects
            .filter(professor=professor)
            .order_by("nome_completo")
        )
