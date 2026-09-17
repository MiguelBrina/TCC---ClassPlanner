from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DisciplinaForm, TemaForm,ConteudoForm
from .models import Aula, Disciplina,Tema


def index(request):
    if request.user.is_authenticated:
        return redirect("painel")

    return render(request, "index.html")


@login_required
def painel(request):
    professor = request.user.professor

    # Disponibilidades configuradas pelo professor
    disponibilidades = (
        professor.disponibilidades
        .all()
        .order_by("dia_semana", "horario")
    )

    # Organiza os horários por dia
    dias = {}

    for disponibilidade in disponibilidades:

        dias.setdefault(
            disponibilidade.dia_semana,
            {
                "nome": disponibilidade.get_dia_semana_display(),
                "horarios": [],
            },
        )

        dias[disponibilidade.dia_semana]["horarios"].append(
            disponibilidade.horario
        )

    # Lista geral de horários
    horarios = sorted(
        {
            disponibilidade.horario
            for disponibilidade in disponibilidades
        }
    )

    # Aulas cadastradas
    aulas = (
        Aula.objects
        .filter(professor=professor)
        .select_related("aluno", "disciplina")
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

#region Disciplinas temas e conteudos crud simples
@login_required
def lista_disciplinas(request):
    professor = request.user.professor 

    disciplinas = Disciplina.objects.filter(
        professor = professor 
    ).order_by("nome")  

    if request.method == "POST":
        form = DisciplinaForm(request.POST)

        if form.is_valid():
            disciplina = form.save(commit=False)
            disciplina.professor = professor
            disciplina.save()

            return redirect("lista_disciplinas")
    else:
        form = DisciplinaForm()

    return render(
        request,
        "core/disciplinas/lista_disciplinas.html",
        {
        "form": form,
        "disciplinas": disciplinas,
        },
    )

@login_required
def lista_temas(request, disciplina_id):
    professor = request.user.professor

    disciplina = get_object_or_404(
        Disciplina,
        id=disciplina_id,
        professor=professor,
    )
    temas = disciplina.temas.all().order_by("nome")

    if request.method == "POST":
        form = TemaForm(request.POST)

        if form.is_valid():
            tema = form.save(commit=False)
            tema.disciplina = disciplina
            tema.save()

            return redirect(
                "lista_temas",
                 disciplina_id=disciplina.id,
            )

    else:
        form = TemaForm()

    return render(
        request,
        "core/temas/lista_temas.html",
        {
            "disciplina": disciplina,
            "temas": temas,
            "form": form,
        },
    )

@login_required
def lista_conteudos(request, tema_id):
    professor = request.user.professor

    tema = get_object_or_404(
    Tema,
    id=tema_id,
    disciplina__professor=professor,
    )
    conteudos =tema.conteudos.all().order_by("nome")

    if request.method == "POST":
        form = ConteudoForm(request.POST)

        if form.is_valid():
            conteudo = form.save(commit=False)
            conteudo.tema= tema
            conteudo.save()

            return redirect(
                "lista_conteudos",
                tema_id=tema.id,
            )

    else:
        form = ConteudoForm()

    return render(
        request,
        "core/conteudos/lista_conteudos.html",
        {
            "tema": tema,
            "conteudos": conteudos,
            "form": form,
        },
    )