from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    ConteudoForm,
    DisciplinaForm,
    TemaForm,
)
from .models import (
    Aula,
    Conteudo,
    Disciplina,
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