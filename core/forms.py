# ============================================================
# IMPORTAÇÕES
# ============================================================

import re

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


# ============================================================
# 1. FORMULÁRIO DE DISCIPLINA
# ============================================================

class DisciplinaForm(forms.ModelForm):
    """
    Cadastra e edita disciplinas.

    Exemplos: Bateria, Piano e Teoria Musical.

    ModelForm gera os campos a partir de um modelo Django.
    Como este formulário só trabalha com nome e cor, não
    precisamos configurar querysets para relacionamentos.

    A view continua responsável por associar a disciplina
    ao professor autenticado.
    """

    class Meta:
        # Modelo que será utilizado para criar ou atualizar registros.
        model = Disciplina

        # Somente estes campos serão apresentados no formulário.
        fields = ["nome", "cor"]

        # widgets controlam como os campos são apresentados no HTML.
        widgets = {
            "cor": forms.TextInput(
                attrs={"type": "color"}
            ),
        }

    def clean_cor(self):
        """
        Valida especificamente o campo cor.

        O Django procura métodos no padrão clean_nome_do_campo
        durante a validação executada por form.is_valid().
        """

        cor = self.cleaned_data["cor"]

        # Uma cor hexadecimal deve ter o formato #RRGGBB.
        # fullmatch exige que todo o texto corresponda ao padrão.
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", cor):
            raise forms.ValidationError(
                "Escolha uma cor válida."
            )

        # Padroniza o valor armazenado em letras minúsculas.
        return cor.lower()


# ============================================================
# 2. FORMULÁRIO DE TEMA
# ============================================================

class TemaForm(forms.ModelForm):
    """
    Cadastra e edita temas dentro de uma disciplina.

    A disciplina não é selecionada neste formulário. A view deve
    receber a disciplina pela URL, verificar sua propriedade e
    atribuí-la ao tema antes de salvar.
    """

    class Meta:
        model = Tema
        fields = ["nome"]


# ============================================================
# 3. FORMULÁRIO DE CONTEÚDO
# ============================================================

class ConteudoForm(forms.ModelForm):
    """
    Cadastra e edita conteúdos dentro de um tema.

    O tema é definido pela view. Isso evita que o usuário escolha
    um tema diferente daquele que está acessando.
    """

    class Meta:
        model = Conteudo
        fields = ["nome"]


# ============================================================
# 4. FORMULÁRIO DE ALUNO
# ============================================================

class AlunoForm(forms.ModelForm):
    """
    Cadastra e edita os dados básicos de um aluno.

    O cadastro de uma pessoa é independente das disciplinas:
    o professor pode cadastrar o aluno agora e matriculá-lo
    em uma ou várias disciplinas depois.

    O campo professor não é disponibilizado ao usuário.
    A view deve atribuir o professor autenticado ao salvar.
    """

    class Meta:
        model = Aluno
        fields = ["nome_completo", "telefone"]


# ============================================================
# 5. FORMULÁRIO DE MATRÍCULA INDIVIDUAL
# ============================================================

class MatriculaForm(forms.ModelForm):
    """
    Representa uma matrícula individual.

    Relaciona:
        Aluno + Disciplina + Data de início

    Este formulário fica disponível para operações que precisem
    lidar com uma matrícula por vez.

    Para a experiência principal do ClassPlanner, na qual várias
    disciplinas são selecionadas de uma vez, utilizaremos também
    MatricularDisciplinasForm.
    """

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
        """
        Recebe o professor autenticado e restringe os dois campos.

        O argumento professor é obrigatório. Dessa forma, o código
        que criar este formulário precisará informar explicitamente
        qual professor está realizando a operação.
        """

        super().__init__(*args, **kwargs)

        self.professor = professor

        # O formulário só aceita alunos pertencentes ao professor.
        self.fields["aluno"].queryset = (
            Aluno.objects
            .filter(professor=professor)
            .order_by("nome_completo")
        )

        # Só oferece disciplinas pertencentes ao mesmo professor.
        self.fields["disciplina"].queryset = (
            Disciplina.objects
            .filter(professor=professor)
            .order_by("nome")
        )

    def clean(self):
        """
        Valida regras que dependem de mais de um campo.

        A validação por campo não é suficiente para verificar
        se o conjunto aluno + disciplina representa uma matrícula
        permitida e ainda não existente.
        """

        dados = super().clean()

        aluno = dados.get("aluno")
        disciplina = dados.get("disciplina")

        if aluno and disciplina:

            # Proteção adicional: aluno e disciplina devem pertencer
            # ao professor que recebeu o formulário.
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

            # Evita cadastrar novamente a mesma combinação.
            #
            # Ao editar uma matrícula, ignoramos o próprio registro.
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
    """
    Permite matricular um aluno em várias disciplinas numa única ação.

    Não está ligado diretamente a um único modelo porque a view
    deverá criar vários objetos Matricula a partir de um envio.

    O fluxo será:
        1. A view verifica o acesso ao aluno.
        2. O formulário apresenta as disciplinas permitidas.
        3. O professor seleciona várias opções.
        4. A view cria uma matrícula por disciplina nova.
        5. A view cria um DiárioDeBordo para cada matrícula.
        6. O professor volta diretamente ao detalhe do aluno.
    """

    disciplinas = forms.ModelMultipleChoiceField(
        # Começa vazio. O queryset permitido será definido no __init__.
        queryset=Disciplina.objects.none(),

        # Exige pelo menos uma seleção.
        required=True,

        # O HTML apresentará uma caixa de seleção para cada disciplina.
        widget=forms.CheckboxSelectMultiple,

        label="Disciplinas",
    )

    data_inicio = forms.DateField(
        required=True,

        # O Django calcula a data inicial quando precisar do valor.
        # Isso apenas preenche o campo; não salva nada no banco.
        initial=timezone.localdate,

        widget=forms.DateInput(
            attrs={"type": "date"}
        ),

        label="Data de início",
    )

    def __init__(self, *args, professor, aluno, **kwargs):
        """
        Configura as disciplinas conforme o contexto do aluno.

        professor e aluno precisam ser fornecidos pela view.
        A view ainda deve recuperar o aluno filtrando pelo professor,
        antes de instanciar este formulário.
        """

        super().__init__(*args, **kwargs)

        self.professor = professor
        self.aluno = aluno

        # Verifica se o aluno pertence ao professor esperado.
        self.aluno_autorizado = (
            aluno.professor_id == professor.pk
        )

        # Só precisamos procurar matrículas existentes se o aluno
        # pertencer ao professor que está realizando a operação.
        if self.aluno_autorizado:
            disciplinas_matriculadas = (
                aluno.matriculas.values_list(
                    "disciplina_id",
                    flat=True,
                )
            )

            # Disponibiliza somente disciplinas do professor
            # em que o aluno ainda não está matriculado.
            disciplinas_permitidas = (
                Disciplina.objects
                .filter(professor=professor)
                .exclude(pk__in=disciplinas_matriculadas)
                .order_by("nome")
            )
        else:
            # Falha de forma segura: aluno não autorizado significa
            # que nenhuma disciplina estará disponível.
            disciplinas_permitidas = Disciplina.objects.none()

        # O queryset também é utilizado para validar os IDs enviados
        # no POST. Não é apenas uma lista visual de opções.
        self.fields["disciplinas"].queryset = (
            disciplinas_permitidas
        )

    def clean(self):
        dados = super().clean()

        # Impede o processamento de matrículas quando o formulário
        # foi construído com um aluno que não pertence ao professor.
        if not self.aluno_autorizado:
            raise forms.ValidationError(
                "Não é permitido matricular disciplinas para este aluno."
            )

        return dados


# ============================================================
# 7. FORMULÁRIO DE AULA
# ============================================================

class AulaForm(forms.ModelForm):
    """
    Cadastra ou edita uma aula.

    O professor é um campo do modelo Aula, mas não aparece
    no formulário. A view define esse campo ao salvar.

    Os campos aluno e disciplina são filtrados pelo professor,
    evitando escolhas de outras contas.
    """

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

        # Validamos a combinação dos campos.
        # Os querysets já filtram os objetos, mas esta conferência
        # deixa explícita a regra de negócio.
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
    """
    Formulário genérico para criar um DiárioDeBordo.

    Cada diário pertence a uma única matrícula, por meio de
    OneToOneField. Por isso, a mesma matrícula não pode possuir
    dois diários diferentes.

    No fluxo planejado, a view criará o diário automaticamente
    ao criar uma matrícula. Assim, normalmente este formulário
    não será mostrado diretamente ao professor.
    """

    class Meta:
        model = DiarioDeBordo
        fields = ["matricula"]

    def __init__(self, *args, professor, **kwargs):
        super().__init__(*args, **kwargs)

        self.professor = professor

        # Filtra matrículas cujos aluno e disciplina pertencem
        # ao professor autenticado.
        matriculas_permitidas = (
            Matricula.objects
            .filter(
                aluno__professor=professor,
                disciplina__professor=professor,
            )
            .select_related("aluno", "disciplina")
        )

        # Ao criar um diário, não oferecemos matrículas que já
        # possuem um diário associado.
        #
        # diary__isnull=True consulta a relação reversa definida
        # por related_name="diario" em Matricula.
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
    """
    Cria ou edita uma anotação de Diário de Bordo.

    Campos:
        - diario
        - data
        - observacao
        - temas
        - conteudos

    O formulário aceita professor e, opcionalmente, um diário
    específico para restringir as opções ainda mais.

    A view deve verificar o acesso à página antes de instanciar
    o formulário.
    """

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

            # Permite marcar vários temas.
            "temas": forms.CheckboxSelectMultiple(),

            # Permite marcar vários conteúdos.
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

        # Se estivermos editando um registro, podemos descobrir
        # seu diário pela instância existente.
        #
        # Isso ajuda a manter as opções da edição dentro da mesma
        # disciplina, mesmo quando a view não passa diario.
        instancia = kwargs.get("instance")

        if diario is None and instancia and instancia.pk:
            diario = instancia.diario

        self.diario_contexto = diario

        # Só consideramos diários cujas matrículas estejam ligadas
        # a alunos e disciplinas do professor autenticado.
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

        # Querysets iniciais de temas e conteúdos do professor.
        temas_permitidos = Tema.objects.filter(
            disciplina__professor=professor,
        ).order_by("nome")

        conteudos_permitidos = Conteudo.objects.filter(
            tema__disciplina__professor=professor,
        ).order_by("nome")

        if diario is not None:
            # Também verificamos se o diário específico pertence
            # ao professor esperado.
            diario_autorizado = (
                diario.matricula.aluno.professor_id == professor.pk
                and diario.matricula.disciplina.professor_id
                == professor.pk
            )

            if diario_autorizado:
                # Se o formulário estiver associado a um diário,
                # limitamos suas opções àquele único diário.
                diarios_permitidos = diarios_permitidos.filter(
                    pk=diario.pk,
                )

                # O diário está associado a uma matrícula e esta
                # identifica a disciplina do registro.
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
                # Se o diário não pertence ao professor, não há
                # opções permitidas para esta operação.
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
        """
        Confere a coerência entre o diário, os temas e os conteúdos.

        Todos podem pertencer ao mesmo professor e, ainda assim,
        pertencer a disciplinas diferentes. Por isso, além do filtro
        por professor, verificamos a disciplina do diário escolhido.
        """

        dados = super().clean()

        diario = dados.get("diario")
        temas = dados.get("temas")
        conteudos = dados.get("conteudos")

        if diario:
            disciplina_id = (
                diario.matricula.disciplina_id
            )

            # Todos os temas selecionados precisam pertencer
            # à disciplina da matrícula correspondente.
            if temas:
                if any(
                    tema.disciplina_id != disciplina_id
                    for tema in temas
                ):
                    self.add_error(
                        "temas",
                        "Selecione somente temas desta disciplina.",
                    )

            # Conteudo pertence a Tema, e Tema pertence a Disciplina.
            # Acessamos a disciplina por meio dessas relações.
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
    """
    Versão específica para registrar uma observação no diário
    correspondente a uma matrícula já identificada pela view.

    O campo diario não aparece no formulário.
    A view descobre o DiárioDeBordo pela matrícula acessada
    e associa o registro ao diário correto ao salvar.

    A disciplina é recebida como contexto para limitar os temas
    e conteúdos disponíveis.
    """

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
            "conteudos": forms.CheckboxSelectMultiple(),
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

        # Não basta receber um objeto Disciplina: ele deve pertencer
        # ao professor que está utilizando o formulário.
        self.disciplina_autorizada = (
            disciplina.professor_id == professor.pk
        )

        if self.disciplina_autorizada:
            # Os temas são limitados à disciplina atual.
            self.fields["temas"].queryset = (
                Tema.objects
                .filter(
                    disciplina=disciplina,
                )
                .order_by("nome")
            )

            # Conteudo não aponta diretamente para Disciplina.
            # Filtramos atravessando sua relação com Tema.
            self.fields["conteudos"].queryset = (
                Conteudo.objects
                .filter(
                    tema__disciplina=disciplina,
                )
                .order_by("nome")
            )
        else:
            # Falha de forma segura se a disciplina não pertencer
            # ao professor esperado.
            self.fields["temas"].queryset = (
                Tema.objects.none()
            )

            self.fields["conteudos"].queryset = (
                Conteudo.objects.none()
            )

    def clean(self):
        dados = super().clean()

        # A view ainda precisa validar e recuperar a matrícula
        # com filtro de professor. Este formulário também recusa
        # uma disciplina que pertença a outra conta.
        if not self.disciplina_autorizada:
            raise forms.ValidationError(
                "Não é permitido registrar informações nesta disciplina."
            )

        return dados


# ============================================================
# 11. FORMULÁRIO DE PAGAMENTO
# ============================================================

class PagamentoForm(forms.ModelForm):
    """
    Cria ou atualiza o estado de pagamento de um aluno.

    O formulário contém aluno, mês de referência e estado pago.

    A mensalidade, o valor da cobrança e os relatórios financeiros
    não são implementados aqui. Este formulário representa somente
    os campos que já existem no modelo Pagamento.
    """

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

        # Não disponibiliza alunos de outros professores.
        self.fields["aluno"].queryset = (
            Aluno.objects
            .filter(professor=professor)
            .order_by("nome_completo")
        )