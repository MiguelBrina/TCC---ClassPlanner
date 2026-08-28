from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import ConfiguracaoAgendaForm
from .models import DisponibilidadeProfessor


@login_required
def configuracao_inicial(request):

    professor = request.user.professor

    if professor.agenda_configurada:
        return redirect("painel")

    if request.method == "POST":

        form = ConfiguracaoAgendaForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                professor.nome_exibicao = form.cleaned_data["nome_exibicao"]

                DisponibilidadeProfessor.objects.filter(
                    professor=professor
                ).delete()

                dias = [
                    (0, "segunda"),
                    (1, "terca"),
                    (2, "quarta"),
                    (3, "quinta"),
                    (4, "sexta"),
                    (5, "sabado"),
                    (6, "domingo"),
                ]

                for numero_dia, nome_dia in dias:

                    if form.cleaned_data.get(nome_dia):

                        DisponibilidadeProfessor.objects.create(
                            professor=professor,
                            dia_semana=numero_dia,
                            hora_inicio=form.cleaned_data[
                                f"{nome_dia}_inicio"
                            ],
                            hora_fim=form.cleaned_data[
                                f"{nome_dia}_fim"
                            ],
                        )

                professor.agenda_configurada = True
                professor.save()

            return redirect("painel")

    else:

        form = ConfiguracaoAgendaForm(
            initial={
                "nome_exibicao": professor.nome_exibicao
            }
        )

    return render(
        request,
        "account/configuracao_inicial.html",
        {"form": form}
    )


@login_required
def pos_login(request):

    professor = request.user.professor

    if not professor.agenda_configurada:
        return redirect("configuracao_inicial")

    return redirect("painel")


