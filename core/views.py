
from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AlunoForm,
    ConteudoForm,
    DisciplinaForm,
    MatricularDisciplinasForm,
    RegistroMatriculaForm,
    TemaForm,
)

from .models import (
    Aluno,
    Aula,
    Conteudo,
    DiarioDeBordo,
    Disciplina,
    Matricula,
    Mensalidade,
    Registro,
    Tema,
)

from account.models import AgendaProfessor, DisponibilidadeProfessor


# ============================================================
# PÁGINA INICIAL
# ============================================================

def index(request):
    if request.user.is_authenticated:
        return redirect("painel")

    return render(request, "index.html")


# ============================================================
# AGENDA
# ============================================================

@login_required
def painel(request):
    professor = request.user.professor

    agenda, _ = AgendaProfessor.objects.get_or_create(
        professor=professor,
        nome="Agenda principal",
    )

    disponibilidades = list(
        DisponibilidadeProfessor.objects
        .filter(
            professor=professor,
            agenda=agenda,
        )
        .select_related(
            "aula__aluno",
            "aula__disciplina",
        )
        .order_by("dia_semana", "horario")
    )

    dias = {}

    for bloco in disponibilidades:
        dias.setdefault(
            bloco.dia_semana,
            {"nome": bloco.get_dia_semana_display()},
        )

    dias = dict(sorted(dias.items()))

    horarios = sorted({
        bloco.horario
        for bloco in disponibilidades
    })

    mapa_disponibilidades = {
        (bloco.dia_semana, bloco.horario): bloco
        for bloco in disponibilidades
    }

    matriculas = list(
        Matricula.objects
        .filter(
            aluno__professor=professor,
            disciplina__professor=professor,
        )
        .select_related("aluno", "disciplina")
        .order_by("aluno__nome_completo", "disciplina__nome")
    )

    alunos = list(
        Aluno.objects
        .filter(professor=professor)
        .order_by("nome_completo")
    )

    if request.method == "POST":

        acao = request.POST.get("acao")

        if acao == "cancelar":
            return redirect("painel")

        if acao == "salvar":

            erro = None
            atribuicoes = []

            for bloco in disponibilidades:

                aluno_id = request.POST.get(
                    f"aluno_{bloco.pk}", ""
                ).strip()

                disciplina_id = request.POST.get(
                    f"disciplina_{bloco.pk}", ""
                ).strip()

                if not aluno_id and not disciplina_id:
                    atribuicoes.append((bloco, None, None))
                    continue

                if not aluno_id or not disciplina_id:
                    erro = (
                        "Selecione um aluno e uma disciplina "
                        "ou deixe os dois campos vazios."
                    )
                    break

                matricula = (
                    Matricula.objects
                    .filter(
                        aluno_id=aluno_id,
                        disciplina_id=disciplina_id,
                        aluno__professor=professor,
                        disciplina__professor=professor,
                    )
                    .select_related("aluno", "disciplina")
                    .first()
                )

                if not matricula:
                    erro = (
                        "A combinação de aluno e disciplina "
                        "é inválida. Confira as matrículas."
                    )
                    break

                atribuicoes.append(
                    (
                        bloco,
                        matricula.aluno,
                        matricula.disciplina,
                    )
                )

            if erro is None:

                try:
                    with transaction.atomic():

                        for bloco, aluno, disciplina in atribuicoes:

                            if aluno is None:

                                Aula.objects.filter(
                                    disponibilidade=bloco
                                ).delete()

                            else:

                                Aula.objects.update_or_create(
                                    disponibilidade=bloco,
                                    defaults={
                                        "professor": professor,
                                        "aluno": aluno,
                                        "disciplina": disciplina,
                                        "data": None,
                                        "horario": None,
                                    },
                                )

                except IntegrityError:
                    erro = (
                        "Não foi possível salvar a agenda. "
                        "Verifique os horários e tente novamente."
                    )

                else:
                    return redirect("painel")

            modo_edicao = True

        else:
            erro = "Ação não reconhecida."
            modo_edicao = True

    else:
        modo_edicao = request.GET.get("editar") == "1"
        erro = None

    grade = []

    for horario in horarios:

        celulas = []

        for numero_dia, dia in dias.items():

            bloco = mapa_disponibilidades.get(
                (numero_dia, horario)
            )

            aula = (
                getattr(bloco, "aula", None)
                if bloco
                else None
            )

            matricula_atual = None

            if aula:
                matricula_atual = next(
                    (
                        item for item in matriculas
                        if item.aluno_id == aula.aluno_id
                        and item.disciplina_id == aula.disciplina_id
                    ),
                    None,
                )

            celulas.append({
                "disponibilidade": bloco,
                "aula": aula,
                "matricula": matricula_atual,
            })

        grade.append({
            "horario": horario,
            "celulas": celulas,
        })

    contexto = {
        "agenda": agenda,
        "dias": dias,
        "grade": grade,
        "alunos": alunos,
        "matriculas": matriculas,
        "modo_edicao": modo_edicao,
        "erro": erro,
    }

    return render(
        request,
        "core/painel.html",
        contexto,
    )


# ============================================================
# DISCIPLINAS
# ============================================================

@login_required
def lista_disciplinas(request):
    professor = request.user.professor

    disciplinas = (
        Disciplina.objects
        .filter(professor=professor)
        .order_by("nome")
    )

    form = DisciplinaForm()

    if request.method == "POST":

        form = DisciplinaForm(request.POST)

        if form.is_valid():

            disciplina = form.save(commit=False)
            disciplina.professor = professor

            try:
                disciplina.save()
                return redirect("lista_disciplinas")

            except IntegrityError:
                form.add_error(
                    "nome",
                    "Já existe uma disciplina com este nome.",
                )

    return render(
        request,
        "core/disciplinas/lista_disciplinas.html",
        {
            "form": form,
            "form_edicao": DisciplinaForm(),
            "disciplinas": disciplinas,
            "disciplina_edicao_id": "",
            "edicao_com_erro": False,
        },
    )


@login_required
def editar_disciplina(request, pk):
    professor = request.user.professor

    disciplina = get_object_or_404(
        Disciplina,
        pk=pk,
        professor=professor,
    )

    if request.method != "POST":
        return redirect("lista_disciplinas")

    form = DisciplinaForm(
        request.POST,
        instance=disciplina,
    )

    if form.is_valid():

        try:
            form.save()
            return redirect("lista_disciplinas")

        except IntegrityError:
            form.add_error(
                "nome",
                "Já existe uma disciplina com este nome.",
            )

    disciplinas = (
        Disciplina.objects
        .filter(professor=professor)
        .order_by("nome")
    )

    return render(
        request,
        "core/disciplinas/lista_disciplinas.html",
        {
            "form": DisciplinaForm(),
            "form_edicao": form,
            "disciplinas": disciplinas,
            "disciplina_edicao_id": disciplina.id,
            "edicao_com_erro": True,
        },
    )


@login_required
def excluir_disciplina(request, pk):
    professor = request.user.professor

    if request.method == "POST":

        disciplina = get_object_or_404(
            Disciplina,
            pk=pk,
            professor=professor,
        )

        disciplina.delete()

    return redirect("lista_disciplinas")


# ============================================================
# TEMAS
# ============================================================

@login_required
def lista_temas(request, disciplina_id):
    professor = request.user.professor

    disciplina = get_object_or_404(
        Disciplina,
        id=disciplina_id,
        professor=professor,
    )

    temas = disciplina.temas.all().order_by("nome")

    form = TemaForm()

    if request.method == "POST":

        form = TemaForm(request.POST)

        if form.is_valid():

            tema = form.save(commit=False)
            tema.disciplina = disciplina

            try:
                tema.save()

                return redirect(
                    "lista_temas",
                    disciplina_id=disciplina.id,
                )

            except IntegrityError:
                form.add_error(
                    "nome",
                    "Já existe um tema com este nome.",
                )

    return render(
        request,
        "core/temas/lista_temas.html",
        {
            "disciplina": disciplina,
            "temas": temas,
            "form": form,
            "form_edicao": TemaForm(),
            "tema_edicao_id": "",
            "edicao_com_erro": False,
        },
    )


@login_required
def editar_tema(request, pk):
    professor = request.user.professor

    tema = get_object_or_404(
        Tema,
        pk=pk,
        disciplina__professor=professor,
    )

    if request.method != "POST":
        return redirect(
            "lista_temas",
            disciplina_id=tema.disciplina.id,
        )

    form = TemaForm(
        request.POST,
        instance=tema,
    )

    if form.is_valid():

        try:
            form.save()

            return redirect(
                "lista_temas",
                disciplina_id=tema.disciplina.id,
            )

        except IntegrityError:
            form.add_error(
                "nome",
                "Já existe um tema com este nome.",
            )

    temas = tema.disciplina.temas.all().order_by("nome")

    return render(
        request,
        "core/temas/lista_temas.html",
        {
            "disciplina": tema.disciplina,
            "temas": temas,
            "form": TemaForm(),
            "form_edicao": form,
            "tema_edicao_id": tema.id,
            "edicao_com_erro": True,
        },
    )


@login_required
def excluir_tema(request, pk):
    professor = request.user.professor

    if request.method == "POST":

        tema = get_object_or_404(
            Tema,
            pk=pk,
            disciplina__professor=professor,
        )

        disciplina_id = tema.disciplina.id
        tema.delete()

        return redirect(
            "lista_temas",
            disciplina_id=disciplina_id,
        )

    return redirect("lista_disciplinas")


# ============================================================
# CONTEÚDOS
# ============================================================

@login_required
def lista_conteudos(request, tema_id):
    professor = request.user.professor

    tema = get_object_or_404(
        Tema,
        id=tema_id,
        disciplina__professor=professor,
    )

    conteudos = tema.conteudos.all().order_by("nome")

    form = ConteudoForm()

    if request.method == "POST":

        form = ConteudoForm(request.POST)

        if form.is_valid():

            conteudo = form.save(commit=False)
            conteudo.tema = tema

            try:
                conteudo.save()

                return redirect(
                    "lista_conteudos",
                    tema_id=tema.id,
                )

            except IntegrityError:
                form.add_error(
                    "nome",
                    "Já existe um conteúdo com este nome.",
                )

    return render(
        request,
        "core/conteudos/lista_conteudos.html",
        {
            "tema": tema,
            "conteudos": conteudos,
            "form": form,
            "form_edicao": ConteudoForm(),
            "conteudo_edicao_id": "",
            "edicao_com_erro": False,
        },
    )


@login_required
def editar_conteudo(request, pk):
    professor = request.user.professor

    conteudo = get_object_or_404(
        Conteudo,
        pk=pk,
        tema__disciplina__professor=professor,
    )

    if request.method != "POST":
        return redirect(
            "lista_conteudos",
            tema_id=conteudo.tema.id,
        )

    form = ConteudoForm(
        request.POST,
        instance=conteudo,
    )

    if form.is_valid():

        try:
            form.save()

            return redirect(
                "lista_conteudos",
                tema_id=conteudo.tema.id,
            )

        except IntegrityError:
            form.add_error(
                "nome",
                "Já existe um conteúdo com este nome.",
            )

    conteudos = conteudo.tema.conteudos.all().order_by("nome")

    return render(
        request,
        "core/conteudos/lista_conteudos.html",
        {
            "tema": conteudo.tema,
            "conteudos": conteudos,
            "form": ConteudoForm(),
            "form_edicao": form,
            "conteudo_edicao_id": conteudo.id,
            "edicao_com_erro": True,
        },
    )


@login_required
def excluir_conteudo(request, pk):
    professor = request.user.professor

    if request.method == "POST":

        conteudo = get_object_or_404(
            Conteudo,
            pk=pk,
            tema__disciplina__professor=professor,
        )

        tema_id = conteudo.tema.id
        conteudo.delete()

        return redirect(
            "lista_conteudos",
            tema_id=tema_id,
        )

    return redirect("lista_disciplinas")


# ============================================================
# ALUNOS
# ============================================================

@login_required
def lista_alunos(request):
    professor = request.user.professor

    busca = request.GET.get("q", "").strip()
    disciplinas_selecionadas = request.GET.getlist("disciplinas")

    alunos = Aluno.objects.filter(professor=professor)

    if busca:
        alunos = alunos.filter(
            nome_completo__icontains=busca
        )

    if disciplinas_selecionadas:
        alunos = alunos.filter(
            matriculas__disciplina__id__in=disciplinas_selecionadas
        ).distinct()

    alunos = alunos.order_by("nome_completo")

    disciplinas = (
        Disciplina.objects
        .filter(professor=professor)
        .order_by("nome")
    )

    return render(
        request,
        "core/alunos/lista_alunos.html",
        {
            "professor": professor,
            "alunos": alunos,
            "busca": busca,
            "disciplinas": disciplinas,
            "disciplinas_selecionadas": disciplinas_selecionadas,
        },
    )


@login_required
def cadastrar_aluno(request):
    professor = request.user.professor

    if request.method == "POST":

        form = AlunoForm(request.POST)

        if form.is_valid():

            aluno = form.save(commit=False)
            aluno.professor = professor
            aluno.save()

            return redirect(
                "detalhe_aluno",
                aluno_id=aluno.pk,
            )

    else:
        form = AlunoForm()

    return render(
        request,
        "core/alunos/cadastrar.html",
        {
            "form": form,
        },
    )


@login_required
def detalhe_aluno(request, aluno_id):
    professor = request.user.professor

    aluno = get_object_or_404(
        Aluno,
        pk=aluno_id,
        professor=professor,
    )

    matriculas = (
        Matricula.objects
        .filter(
            aluno=aluno,
            disciplina__professor=professor,
        )
        .select_related("disciplina")
        .order_by("disciplina__nome")
    )

    temas_conhecidos = (
        Tema.objects
        .filter(
            registros__diario__matricula__aluno=aluno,
            disciplina__professor=professor,
        )
        .select_related("disciplina")
        .distinct()
        .order_by("disciplina__nome", "nome")
    )

    return render(
        request,
        "core/alunos/detalhe.html",
        {
            "aluno": aluno,
            "matriculas": matriculas,
            "temas_conhecidos": temas_conhecidos,
        },
    )


@login_required
def editar_aluno(request, aluno_id):
    professor = request.user.professor

    aluno = get_object_or_404(
        Aluno,
        pk=aluno_id,
        professor=professor,
    )

    if request.method == "POST":

        form = AlunoForm(
            request.POST,
            instance=aluno,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "detalhe_aluno",
                aluno_id=aluno.pk,
            )

    else:
        form = AlunoForm(instance=aluno)

    return render(
        request,
        "core/alunos/editar.html",
        {
            "aluno": aluno,
            "form": form,
        },
    )


@login_required
def excluir_aluno(request, aluno_id):
    professor = request.user.professor

    if request.method == "POST":

        aluno = get_object_or_404(
            Aluno,
            pk=aluno_id,
            professor=professor,
        )

        aluno.delete()

    return redirect("lista_alunos")


# ============================================================
# MATRÍCULA MÚLTIPLA
# ============================================================

@login_required
def matricular_aluno(request, aluno_id):
    professor = request.user.professor

    aluno = get_object_or_404(
        Aluno,
        pk=aluno_id,
        professor=professor,
    )

    if request.method == "POST":

        form = MatricularDisciplinasForm(
            request.POST,
            professor=professor,
            aluno=aluno,
        )

        if form.is_valid():

            data_inicio = form.cleaned_data["data_inicio"]
            disciplinas = form.cleaned_data["disciplinas"]
            valor_mensal = form.cleaned_data["valor_mensal"]

            try:
                with transaction.atomic():

                    for disciplina in disciplinas:

                        matricula, criada = (
                            Matricula.objects.get_or_create(
                                aluno=aluno,
                                disciplina=disciplina,
                                defaults={
                                    "data_inicio": data_inicio,
                                    "valor_mensal": valor_mensal,
                                },
                            )
                        )

                        DiarioDeBordo.objects.get_or_create(
                            matricula=matricula,
                        )

            except IntegrityError:
                form.add_error(
                    None,
                    "Não foi possível concluir todas as matrículas. "
                    "Verifique os dados e tente novamente.",
                )

            else:
                return redirect(
                    "detalhe_aluno",
                    aluno_id=aluno.pk,
                )

    else:
        form = MatricularDisciplinasForm(
            professor=professor,
            aluno=aluno,
        )

    return render(
        request,
        "core/alunos/matricular.html",
        {
            "aluno": aluno,
            "form": form,
        },
    )


# ============================================================
# DIÁRIO DE BORDO
# ============================================================

@login_required
def diario_aluno(request, aluno_id, matricula_id):
    professor = request.user.professor

    aluno = get_object_or_404(
        Aluno,
        pk=aluno_id,
        professor=professor,
    )

    matricula = get_object_or_404(
        Matricula.objects.select_related(
            "aluno",
            "disciplina",
        ),
        pk=matricula_id,
        aluno=aluno,
        disciplina__professor=professor,
    )

    diario, _ = DiarioDeBordo.objects.get_or_create(
        matricula=matricula,
    )

    if request.method == "POST":

        form = RegistroMatriculaForm(
            request.POST,
            professor=professor,
            disciplina=matricula.disciplina,
        )

        if form.is_valid():

            registro = form.save(commit=False)
            registro.diario = diario

            with transaction.atomic():
                registro.save()
                form.save_m2m()

            return redirect(
                "diario_aluno",
                aluno_id=aluno.pk,
                matricula_id=matricula.pk,
            )

    else:
        form = RegistroMatriculaForm(
            professor=professor,
            disciplina=matricula.disciplina,
        )

    registros = (
        diario.registros
        .prefetch_related("temas", "conteudos")
        .all()
    )

    return render(
        request,
        "core/diario/registro_diario.html",
        {
            "aluno": aluno,
            "matricula": matricula,
            "disciplina": matricula.disciplina,
            "diario": diario,
            "registros": registros,
            "form": form,
        },
    )


# ============================================================
# EXCLUIR MATRÍCULA
# ============================================================

@login_required
def excluir_matricula(request, aluno_id, matricula_id):
    professor = request.user.professor

    if request.method == "POST":

        matricula = get_object_or_404(
            Matricula,
            pk=matricula_id,
            aluno_id=aluno_id,
            aluno__professor=professor,
            disciplina__professor=professor,
        )

        matricula.delete()

    return redirect(
        "detalhe_aluno",
        aluno_id=aluno_id,
    )


# ============================================================
# FINANCEIRO - FUNÇÕES AUXILIARES
# ============================================================

def _competencia_da_requisicao(request):
    valor = request.GET.get("mes") or request.POST.get("mes")

    if valor:
        try:
            ano, mes = map(int, valor.split("-"))

            if 1 <= mes <= 12 and 2000 <= ano <= 2100:
                return date(ano, mes, 1)

        except (ValueError, TypeError):
            pass

    hoje = timezone.localdate()

    return date(hoje.year, hoje.month, 1)


def _mensalidades_da_competencia(professor, competencia):
    return (
        Mensalidade.objects
        .filter(
            competencia=competencia,
            matricula__aluno__professor=professor,
            matricula__disciplina__professor=professor,
        )
        .select_related(
            "matricula__aluno",
            "matricula__disciplina",
        )
        .order_by(
            "matricula__aluno__nome_completo",
            "matricula__disciplina__nome",
        )
    )


# ============================================================
# FINANCEIRO - TELA PRINCIPAL
# ============================================================

@login_required
def financeiro_matricula(request, aluno_id, matricula_id):
    """Gerencia as cobranças de uma matrícula específica."""
    professor = request.user.professor

    competencia = _competencia_da_requisicao(request)
    hoje = timezone.localdate()
    competencia_atual = hoje.replace(day=1)

    matricula = get_object_or_404(
        Matricula.objects.select_related("aluno", "disciplina"),
        pk=matricula_id,
        aluno_id=aluno_id,
        aluno__professor=professor,
        disciplina__professor=professor,
    )

    url_financeiro = (
        f"/alunos/{aluno_id}/matriculas/{matricula_id}/financeiro/"
    )

    def voltar_financeiro():
        return redirect(f"{url_financeiro}?mes={competencia:%Y-%m}")

    def render_financeiro(erro=None):
        historico = list(
            Mensalidade.objects
            .filter(matricula=matricula)
            .order_by("-competencia", "-criado_em")
        )

        total_pagas = sum(1 for item in historico if item.pago_em)
        total_atrasadas = sum(
            1 for item in historico
            if not item.pago_em and item.vencimento < hoje
        )

        mensalidades_mes = [
            item for item in historico
            if item.competencia.year == competencia.year
            and item.competencia.month == competencia.month
        ]

        mensalidade_atual = next(
            (
                item for item in historico
                if item.competencia == competencia_atual
            ),
            None,
        )
        status_mes_atual = (
            "Pago" if mensalidade_atual and mensalidade_atual.pago_em
            else "Pendente"
        )

        return render(
            request,
            "core/financeiro/financeiro.html",
            {
                "aluno": matricula.aluno,
                "matricula": matricula,
                "competencia": competencia,
                "mes_input": competencia.strftime("%Y-%m"),
                "competencia_atual": competencia_atual,
                "mensalidades": historico,
                "mensalidades_mes": mensalidades_mes,
                "total_pagas": total_pagas,
                "total_atrasadas": total_atrasadas,
                "status_mes_atual": status_mes_atual,
                "pendentes_mes_atual": (
                    1 if status_mes_atual == "Pendente" else 0
                ),
                "matriculas_sem_valor": (
                    [matricula] if matricula.valor_mensal <= 0 else []
                ),
                "erro": erro,
            },
        )

    if request.method == "POST":
        acao = request.POST.get("acao")

        # Define o valor de cada parcela e quantas cobranças mensais gerar.
        if acao == "salvar_valor":
            try:
                valor = Decimal(
                    request.POST.get("valor_mensal", "").replace(",", ".")
                )
                quantidade = int(request.POST.get("quantidade_parcelas", "1"))

                if (
                    not valor.is_finite()
                    or valor <= 0
                    or valor > Decimal("99999999.99")
                ):
                    raise InvalidOperation

                if quantidade < 1 or quantidade > 60:
                    raise ValueError

            except (InvalidOperation, ValueError, TypeError, AttributeError):
                return render_financeiro(
                    "Informe um valor válido e uma quantidade de 1 a 60 parcelas."
                )

            # O valor padrão passa a ser o valor de cada parcela mensal.
            matricula.valor_mensal = valor
            matricula.save(update_fields=["valor_mensal"])

            # Gera uma cobrança por mês, a partir do mês selecionado.
            # Registros que já existem não são sobrescritos nem duplicados.
            with transaction.atomic():
                for deslocamento in range(quantidade):
                    indice_mes = competencia.year * 12 + (competencia.month - 1) + deslocamento
                    ano = indice_mes // 12
                    mes = (indice_mes % 12) + 1
                    data_competencia = date(ano, mes, 1)

                    Mensalidade.objects.get_or_create(
                        matricula=matricula,
                        competencia=data_competencia,
                        defaults={"valor": valor},
                    )

            return voltar_financeiro()

        # Altera o valor de uma cobrança individual ainda não paga.
        if acao == "alterar_valor_cobranca":
            mensalidade = get_object_or_404(
                Mensalidade,
                pk=request.POST.get("mensalidade_id"),
                matricula=matricula,
            )

            if mensalidade.pago_em:
                return voltar_financeiro()

            try:
                novo_valor = Decimal(
                    request.POST.get("valor", "").replace(",", ".")
                )
                if (
                    not novo_valor.is_finite()
                    or novo_valor <= 0
                    or novo_valor > Decimal("99999999.99")
                ):
                    raise InvalidOperation
            except (InvalidOperation, ValueError, TypeError, AttributeError):
                return render_financeiro(
                    "Informe um valor válido para a mensalidade."
                )

            mensalidade.valor = novo_valor
            mensalidade.save(update_fields=["valor"])
            return voltar_financeiro()

        # Confirma o pagamento de uma cobrança.
        if acao == "confirmar_pagamento":
            mensalidade = get_object_or_404(
                Mensalidade,
                pk=request.POST.get("mensalidade_id"),
                matricula=matricula,
            )

            if not mensalidade.pago_em:
                mensalidade.pago_em = timezone.now()
                mensalidade.save(update_fields=["pago_em"])

            return voltar_financeiro()

        # Exclui somente o registro selecionado no histórico.
        if acao == "excluir_mensalidade":
            mensalidade = get_object_or_404(
                Mensalidade,
                pk=request.POST.get("mensalidade_id"),
                matricula=matricula,
            )
            mensalidade.delete()
            return voltar_financeiro()

    return render_financeiro()


# ============================================================
# RECIBO DE PAGAMENTO EM PDF
# ============================================================

@login_required
def recibo_mensalidade_pdf(request, mensalidade_id):
    professor = request.user.professor

    mensalidade = get_object_or_404(
        Mensalidade.objects.select_related(
            "matricula__aluno",
            "matricula__disciplina",
        ),
        pk=mensalidade_id,
        matricula__aluno__professor=professor,
        matricula__disciplina__professor=professor,
    )

    matricula = mensalidade.matricula

    url_financeiro = (
        f"/alunos/{matricula.aluno_id}/"
        f"matriculas/{matricula.pk}/financeiro/"
    )

    # Recibo só pode ser emitido depois da confirmação do pagamento.
    if not mensalidade.pago_em:
        return redirect(
            f"{url_financeiro}?mes={mensalidade.competencia:%Y-%m}"
        )

    from xml.sax.saxutils import escape

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle,
    )
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        HRFlowable,
    )

    buffer = BytesIO()

    nome_professor_original = (
        professor.nome_exibicao.strip()
        or professor.usuario.get_full_name().strip()
        or professor.usuario.email
    )

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25 * mm,
        leftMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
        title="Recibo de pagamento",
        author=nome_professor_original,
    )

    # Identidade visual neutra e profissional.
    cor_texto = colors.HexColor("#252525")
    cor_secundaria = colors.HexColor("#666666")
    cor_linha = colors.HexColor("#E5E5E5")
    cor_fundo = colors.HexColor("#F7F7F5")
    cor_destaque = colors.HexColor("#34443A")

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "ReciboTitulo",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=24,
        alignment=TA_LEFT,
        textColor=cor_texto,
        spaceAfter=4,
    )

    subtitulo_style = ParagraphStyle(
        "ReciboSubtitulo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=cor_secundaria,
    )

    secao_style = ParagraphStyle(
        "ReciboSecao",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=cor_texto,
        spaceBefore=5,
        spaceAfter=7,
    )

    texto_style = ParagraphStyle(
        "ReciboTexto",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=cor_texto,
    )

    valor_style = ParagraphStyle(
        "ReciboValor",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=26,
        textColor=cor_destaque,
    )

    pequeno_style = ParagraphStyle(
        "ReciboPequeno",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=12,
        textColor=cor_secundaria,
    )

    nome_professor = escape(nome_professor_original)
    nome_aluno = escape(matricula.aluno.nome_completo)
    nome_disciplina = escape(matricula.disciplina.nome)

    # CPF é opcional. Só aparece no recibo se estiver preenchido.
    cpf_professor = (professor.cpf or "").strip()

    valor_formatado = (
        f"R$ {mensalidade.valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    data_emissao = timezone.localtime().strftime("%d/%m/%Y às %H:%M")
    data_pagamento = timezone.localtime(
        mensalidade.pago_em
    ).strftime("%d/%m/%Y às %H:%M")

    mes_referencia = mensalidade.competencia.strftime("%m/%Y")

    story = [
        Paragraph("RECIBO DE PAGAMENTO", titulo_style),
        Paragraph("COMPROVANTE DE MENSALIDADE", subtitulo_style),
        Spacer(1, 8 * mm),
        HRFlowable(width="100%", thickness=1, color=cor_linha),
        Spacer(1, 8 * mm),
        Paragraph("DADOS DO PROFESSOR", secao_style),
    ]

    dados_professor = [
        [
            Paragraph("<b>Professor</b>", texto_style),
            Paragraph(nome_professor, texto_style),
        ],
    ]

    if cpf_professor:
        dados_professor.append([
            Paragraph("<b>CPF</b>", texto_style),
            Paragraph(escape(cpf_professor), texto_style),
        ])

    tabela_professor = Table(
        dados_professor,
        colWidths=[38 * mm, 122 * mm],
    )

    tabela_professor.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cor_fundo),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, cor_linha),
    ]))

    story.extend([
        tabela_professor,
        Spacer(1, 8 * mm),
        Paragraph("DADOS DO PAGAMENTO", secao_style),
    ])

    dados_pagamento = [
        [
            Paragraph("<b>Aluno</b>", texto_style),
            Paragraph(nome_aluno, texto_style),
        ],
        [
            Paragraph("<b>Disciplina</b>", texto_style),
            Paragraph(nome_disciplina, texto_style),
        ],
        [
            Paragraph("<b>Mês de referência</b>", texto_style),
            Paragraph(mes_referencia, texto_style),
        ],
        [
            Paragraph("<b>Data da confirmação</b>", texto_style),
            Paragraph(data_pagamento, texto_style),
        ],
    ]

    tabela_pagamento = Table(
        dados_pagamento,
        colWidths=[48 * mm, 112 * mm],
    )

    tabela_pagamento.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, cor_linha),
    ]))

    story.extend([
        tabela_pagamento,
        Spacer(1, 10 * mm),
    ])

    caixa_valor = Table(
        [[
            Paragraph("VALOR RECEBIDO", pequeno_style),
            Paragraph(valor_formatado, valor_style),
        ]],
        colWidths=[65 * mm, 95 * mm],
    )

    caixa_valor.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cor_fundo),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 13),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 13),
    ]))

    story.extend([
        caixa_valor,
        Spacer(1, 12 * mm),
        Paragraph(
            "Declaramos que o valor acima foi recebido e que o "
            "pagamento referente ao mês indicado foi confirmado "
            "pelo professor responsável.",
            texto_style,
        ),
        Spacer(1, 12 * mm),
        HRFlowable(width="100%", thickness=0.7, color=cor_linha),
        Spacer(1, 5 * mm),
        Paragraph(
            f"Data de emissão: {data_emissao}",
            pequeno_style,
        ),
        Paragraph(
            "Recibo gerado pelo sistema ClassPlanner.",
            pequeno_style,
        ),
    ])

    pdf.build(story)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        'attachment; filename="recibo-mensalidade.pdf"'
    )

    return response
