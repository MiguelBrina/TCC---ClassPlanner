from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import DisciplinaForm
from .models import Aula,Disciplina
from django.shortcuts import render, redirect, get_object_or_404
#from django.shortcuts import render, redirect, get_object_or_404
from .models import Disciplina, Professor

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
    professor = get_object_or_404(Professor, user=request.user)

    if request.method == "POST":
        disciplina_id = request.POST.get("id")
        nome = request.POST.get("nome")
        cor = request.POST.get("cor", "#3b82f6")

        if disciplina_id:
            # EDITAR
            disciplina = get_object_or_404(Disciplina, pk=disciplina_id, professor=professor)
            disciplina.nome = nome
            disciplina.cor = cor
            disciplina.save()
        else:
            # ADICIONAR NOVA
            Disciplina.objects.create(
                professor=professor,
                nome=nome,
                cor=cor
            )

        return redirect("lista_disciplinas")

    disciplinas = Disciplina.objects.filter(professor=professor)
    return render(request, "core/disciplinas/lista_disciplinas.html", {"disciplinas": disciplinas})


@login_required
def excluir_disciplina(request, pk):
    if request.method == "POST":
        disciplina = get_object_or_404(Disciplina, pk=pk, professor__user=request.user)
        disciplina.delete()
    return redirect("lista_disciplinas")