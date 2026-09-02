from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Aula


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