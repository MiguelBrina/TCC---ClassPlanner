from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

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
    Registro,
    Tema,
)

def index(request):
    if request.user.is_authenticated:
        return redirect("painel")

    return render(
        request,
        "index.html",
    )


@login_required
def painel(request):
    professor = request.user.professor

    disponibilidades = (
        professor.disponibilidades
        .all()
        .order_by(
            "dia_semana",
            "horario",
        )
    )

    dias = {}

    for disponibilidade in disponibilidades:
        dias.setdefault(
            disponibilidade.dia_semana,
            {
                "nome": (
                    disponibilidade
                    .get_dia_semana_display()
                ),
                "horarios": [],
            },
        )

        dias[
            disponibilidade.dia_semana
        ]["horarios"].append(
            disponibilidade.horario
        )

    horarios = sorted(
        {
            disponibilidade.horario
            for disponibilidade in disponibilidades
        }
    )

    aulas = (
        Aula.objects
        .filter(professor=professor)
        .select_related(
            "aluno",
            "disciplina",
        )
    )

    contexto = {
        "dias": dias,
        "horarios": horarios,
        "aulas": aulas,
    }

    return render(
        request,
        "core/painel.html",
        contexto,
    )


#region Disciplinas, temas e conteúdos


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
            disciplina = form.save(
                commit=False
            )

            disciplina.professor = professor

            try:
                disciplina.save()

                return redirect(
                    "lista_disciplinas"
                )

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
        return redirect(
            "lista_disciplinas"
        )

    form = DisciplinaForm(
        request.POST,
        instance=disciplina,
    )

    if form.is_valid():
        try:
            form.save()

            return redirect(
                "lista_disciplinas"
            )

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

    return redirect(
        "lista_disciplinas"
    )


@login_required
def lista_temas(request, disciplina_id):
    professor = request.user.professor

    disciplina = get_object_or_404(
        Disciplina,
        id=disciplina_id,
        professor=professor,
    )

    temas = (
        disciplina.temas
        .all()
        .order_by("nome")
    )

    form = TemaForm()

    if request.method == "POST":
        form = TemaForm(request.POST)

        if form.is_valid():
            tema = form.save(
                commit=False
            )

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

    temas = (
        tema.disciplina.temas
        .all()
        .order_by("nome")
    )

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

    return redirect(
        "lista_disciplinas"
    )


@login_required
def lista_conteudos(request, tema_id):
    professor = request.user.professor

    tema = get_object_or_404(
        Tema,
        id=tema_id,
        disciplina__professor=professor,
    )

    conteudos = (
        tema.conteudos
        .all()
        .order_by("nome")
    )

    form = ConteudoForm()

    if request.method == "POST":
        form = ConteudoForm(request.POST)

        if form.is_valid():
            conteudo = form.save(
                commit=False
            )

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

    conteudos = (
        conteudo.tema.conteudos
        .all()
        .order_by("nome")
    )

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

    return redirect(
        "lista_disciplinas"
    )

#endregion
# ============================================================
# ALUNOS
# ============================================================

@login_required
def lista_alunos(request):
    """
    Exibe os alunos do professor autenticado.

    O filtro por professor é essencial: não devemos misturar
    os alunos pertencentes às contas de professores diferentes.
    """

    professor = request.user.professor

    alunos = (
        Aluno.objects
        .filter(professor=professor)
        .order_by("nome_completo")
    )

    return render(
        request,
        "core/alunos/lista_alunos.html",
        {
            "professor": professor,
            "alunos": alunos,

        },
    )


@login_required
def cadastrar_aluno(request):
    """
    Exibe o formulário de cadastro e salva um aluno válido.

    GET  -> apresenta o formulário.
    POST -> valida e tenta salvar os dados enviados.
    """

    professor = request.user.professor

    if request.method == "POST":
        form = AlunoForm(request.POST)

        if form.is_valid():
            # commit=False cria o objeto em memória, mas ainda
            # não o grava no banco de dados.
            aluno = form.save(commit=False)

            # O professor é definido pelo servidor, nunca por
            # um campo enviado pelo navegador.
            aluno.professor = professor

            aluno.save()

            # Após cadastrar, vamos ao detalhe para permitir
            # a matrícula e o acesso direto aos diários.
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
    """
    Mostra os dados do aluno e suas disciplinas matriculadas.

    A matrícula é um relacionamento interno. Por isso, a tela
    apresenta o acesso aos diários diretamente, sem exigir que
    o professor navegue por uma aba de matrículas.
    """

    professor = request.user.professor

    # O aluno só pode ser encontrado se pertencer ao professor.
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

    return render(
        request,
        "core/alunos/detalhe.html",
        {
            "aluno": aluno,
            "matriculas": matriculas,
        },
    )


@login_required
def editar_aluno(request, aluno_id):
    """
    Edita os dados de um aluno já cadastrado.

    O professor continua sendo o mesmo, pois esse campo não
    faz parte do AlunoForm.
    """

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
        # instance preenche o formulário com os dados existentes.
        form = AlunoForm(instance=aluno)

    return render(
        request,
        "core/alunos/editar.html",
        {
            "aluno": aluno,
            "form": form,
        },
    )


# ============================================================
# MATRÍCULA MÚLTIPLA — FLUXO INTERNO
# ============================================================

@login_required
def matricular_aluno(request, aluno_id):
    """
    Permite selecionar várias disciplinas para um único aluno.

    Após validar o formulário:
        1. Cria ou recupera cada matrícula.
        2. Cria ou recupera o DiárioDeBordo correspondente.
        3. Redireciona diretamente ao detalhe do aluno.

    Não existe uma tela intermediária de matrículas.
    """

    professor = request.user.professor

    # A autorização acontece antes da criação do formulário.
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

            try:
                # Tudo dentro deste bloco é tratado como uma
                # transação: falhas provocam o rollback.
                with transaction.atomic():

                    for disciplina in disciplinas:
                        # get_or_create evita gerar outra matrícula
                        # para um relacionamento já existente.
                        matricula, criada = (
                            Matricula.objects.get_or_create(
                                aluno=aluno,
                                disciplina=disciplina,
                                defaults={
                                    "data_inicio": data_inicio,
                                },
                            )
                        )

                        # Cada matrícula precisa de exatamente
                        # um DiárioDeBordo.
                        #
                        # O OneToOneField do modelo também reforça
                        # essa regra no banco de dados.
                        DiarioDeBordo.objects.get_or_create(
                            matricula=matricula,
                        )

            except IntegrityError:
                # Uma mensagem de erro é adicionada ao formulário.
                # O usuário permanece na tela e pode tentar novamente.
                form.add_error(
                    None,
                    "Não foi possível concluir todas as matrículas. "
                    "Verifique os dados e tente novamente.",
                )

            else:
                # Retorno direto ao aluno, onde os diários estarão
                # disponíveis para acesso.
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
    """
    Abre o diário da disciplina associada à matrícula.

    O aluno e a matrícula são recuperados com filtros de
    propriedade para impedir o acesso cruzado entre professores.
    """
    print("=== DIAGNÓSTICO DE SESSÃO ===")
    print("Usuário autenticado:", request.user.is_authenticated)
    print("ID do usuário:", request.user.id)
    print("Chave da sessão:", request.session.session_key)
    print("Sessão existe:", request.session.exists(
        request.session.session_key
    ))
    print("=============================")


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

    # Garante que a matrícula tenha um diário.
    # Isso também permite abrir uma matrícula antiga que ainda
    # não tenha recebido seu DiárioDeBordo.
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
            # O formulário não permite selecionar o diário.
            # A view define a associação com o diário correto.
            registro = form.save(commit=False)
            registro.diario = diario

            with transaction.atomic():
                registro.save()

                # Como temas e conteúdos são ManyToManyField,
                # suas relações são gravadas após salvar o registro.
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