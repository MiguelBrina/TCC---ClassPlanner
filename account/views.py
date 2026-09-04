from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import (
    ConfiguracaoAgendaForm,
    ExclusaoContaForm,
)
from .models import DisponibilidadeProfessor


@login_required
def configuracao_inicial(request):
    professor, _ = request.user.professor.__class__.objects.get_or_create(
        usuario=request.user
    )

    if professor.agenda_configurada:
        return redirect("painel")

    if request.method == "POST":
        form = ConfiguracaoAgendaForm(request.POST)

        if form.is_valid():
            with transaction.atomic():

                professor.nome_exibicao = (
                    form.cleaned_data["nome_exibicao"]
                )

                DisponibilidadeProfessor.objects.filter(
                    professor=professor
                ).delete()

                dias = form.cleaned_data["dias"]
                horarios = form.cleaned_data["horarios"]

                numeros_dias = {
                    "segunda": 0,
                    "terca": 1,
                    "quarta": 2,
                    "quinta": 3,
                    "sexta": 4,
                    "sabado": 5,
                    "domingo": 6,
                }

                for nome_dia in dias:

                    numero_dia = numeros_dias[nome_dia]

                    for horario in horarios:

                        DisponibilidadeProfessor.objects.create(
                            professor=professor,
                            dia_semana=numero_dia,
                            horario=horario["horario"],
                        )

                professor.agenda_configurada = True
                professor.save()

            return redirect("painel")

    else:
        form = ConfiguracaoAgendaForm(
            initial={
                "nome_exibicao": professor.nome_exibicao,
                "dias": [],
                "horarios": [],
            }
        )

    return render(
        request,
        "account/configuracao_inicial.html",
        {
            "form": form,
        },
    )


@login_required
def pos_login(request):
    professor, _ = request.user.professor.__class__.objects.get_or_create(
        usuario=request.user
    )

    if not professor.agenda_configurada:
        return redirect("configuracao_inicial")

    return redirect("painel")


@login_required
def configuracoes(request):
    professor, _ = request.user.professor.__class__.objects.get_or_create(
        usuario=request.user
    )

    form_exclusao = ExclusaoContaForm(
    professor=professor
    )

    disponibilidades = (
        professor.disponibilidades
        .all()
        .order_by("dia_semana", "horario")
    )

    dias = sorted(
        set(
            disponibilidade.dia_semana
            for disponibilidade in disponibilidades
        )
    )

    horarios = sorted(
        set(
            disponibilidade.horario
            for disponibilidade in disponibilidades
        )
    )

    if request.method == "POST":

        form = ConfiguracaoAgendaForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                professor.nome_exibicao = (
                    form.cleaned_data["nome_exibicao"]
                )

                professor.save()

                DisponibilidadeProfessor.objects.filter(
                    professor=professor
                ).delete()

                numeros_dias = {
                    "segunda": 0,
                    "terca": 1,
                    "quarta": 2,
                    "quinta": 3,
                    "sexta": 4,
                    "sabado": 5,
                    "domingo": 6,
                }

                for nome_dia in form.cleaned_data["dias"]:

                    numero_dia = numeros_dias[nome_dia]

                    for horario in form.cleaned_data["horarios"]:

                        DisponibilidadeProfessor.objects.create(
                            professor=professor,
                            dia_semana=numero_dia,
                            horario=horario["horario"],
                        )

            return redirect("configuracoes")

    else:

        nomes_dias = {
            0: "segunda",
            1: "terca",
            2: "quarta",
            3: "quinta",
            4: "sexta",
            5: "sabado",
            6: "domingo",
        }

        dias_iniciais = [
            nomes_dias[dia]
            for dia in dias
        ]

        horarios_iniciais = [
            {
                "horario": horario.strftime("%H:%M")
            }
            for horario in horarios
        ]

        form = ConfiguracaoAgendaForm(
            initial={
                "nome_exibicao": professor.nome_exibicao,
                "dias": dias_iniciais,
                "horarios": horarios_iniciais,
            }
        )

    return render(
        request,
        "account/configuracoes.html",
        {
            "form": form,
            "professor": professor,
            "form_exclusao": form_exclusao,
        },
    )


@login_required
def excluir_conta(request):
    professor = request.user.professor

    if request.method == "POST":

        form = ExclusaoContaForm(
            request.POST,
            professor=professor,
        )

        if form.is_valid():

            usuario = request.user

            logout(request)
            usuario.delete()

            return redirect("index")

    else:

        form = ExclusaoContaForm(
            professor=professor,
        )

    return render(
        request,
        "account/configuracoes.html",
        {
            "form": ConfiguracaoAgendaForm(
                 initial={
                    "nome_exibicao": professor.nome_exibicao,
            }
        ),
        "form_exclusao": form,
        "professor": professor,
        },
)