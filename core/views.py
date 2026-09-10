from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import DisciplinaForm
from .models import Aula,Disciplina


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

#Disciplinas temas e conteudos crud simples
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