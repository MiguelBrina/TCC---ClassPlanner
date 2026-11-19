
# Importa a função que encerra a sessão do usuário.
from django.contrib.auth import logout

# Impede que pessoas não autenticadas acessem essas páginas.
from django.contrib.auth.decorators import login_required

# Permite executar várias alterações no banco como uma única operação.
from django.db import transaction

# Funções usadas para redirecionar e renderizar páginas.
from django.shortcuts import redirect, render

# Formulários utilizados nesta parte do sistema.
from .forms import (
    ConfiguracaoAgendaForm,
    ExclusaoContaForm,
)

# Modelos relacionados ao professor e à agenda.
from .models import (
    Professor,
    AgendaProfessor,
    DisponibilidadeProfessor,
)


# Converte os nomes dos dias para os números utilizados pelo Django.
NUMEROS_DIAS = {
    "segunda": 0,
    "terca": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sabado": 5,
    "domingo": 6,
}


# Recupera ou cria a agenda principal do professor.
def obter_agenda_principal(professor):
    agenda, _ = AgendaProfessor.objects.get_or_create(
        professor=professor,
        nome="Agenda principal",
    )

    return agenda


# Atualiza os horários da agenda sem recriar os que continuam iguais.
def salvar_disponibilidades(professor, agenda, dias, horarios):

    # Monta todas as combinações de dia e horário selecionadas.
    horarios_desejados = set()

    for nome_dia in dias:
        numero_dia = NUMEROS_DIAS[nome_dia]

        for horario in horarios:
            horarios_desejados.add(
                (numero_dia, horario["horario"])
            )

    # Busca os horários que já existem na agenda principal.
    disponibilidades_atuais = DisponibilidadeProfessor.objects.filter(
        professor=professor,
        agenda=agenda,
    )

    # Organiza os horários existentes para facilitar a comparação.
    horarios_atuais = {}

    for disponibilidade in disponibilidades_atuais:
        chave = (
            disponibilidade.dia_semana,
            disponibilidade.horario.strftime("%H:%M"),
        )

        horarios_atuais[chave] = disponibilidade

    # Remove somente os horários que deixaram de ser selecionados.
    for chave, disponibilidade in horarios_atuais.items():
        if chave not in horarios_desejados:
            disponibilidade.delete()

    # Cria somente os horários que ainda não existem.
    for numero_dia, horario in horarios_desejados:
        chave = (numero_dia, horario)

        if chave not in horarios_atuais:
            DisponibilidadeProfessor.objects.create(
                professor=professor,
                agenda=agenda,
                dia_semana=numero_dia,
                horario=horario,
            )


# Configuração inicial realizada pelo professor no primeiro acesso.
@login_required
def configuracao_inicial(request):

    # Garante que o usuário tenha um cadastro de professor.
    professor, _ = Professor.objects.get_or_create(
        usuario=request.user
    )

    # Se já configurou a agenda, não precisa repetir essa etapa.
    if professor.agenda_configurada:
        return redirect("painel")

    # Recupera ou cria a agenda principal.
    agenda = obter_agenda_principal(professor)

    # Verifica se o formulário foi enviado.
    if request.method == "POST":
        form = ConfiguracaoAgendaForm(request.POST)

        # Continua somente se os dados forem válidos.
        if form.is_valid():

            # Garante que as alterações sejam salvas juntas.
            with transaction.atomic():

                # Atualiza o nome de exibição do professor.
                professor.nome_exibicao = (
                    form.cleaned_data["nome_exibicao"]
                )

                # Salva os dias e horários escolhidos.
                salvar_disponibilidades(
                    professor,
                    agenda,
                    form.cleaned_data["dias"],
                    form.cleaned_data["horarios"],
                )

                # Marca que a configuração inicial foi concluída.
                professor.agenda_configurada = True
                professor.save()

            # Depois da configuração, segue para o painel.
            return redirect("painel")

    else:
        # Formulário vazio para o primeiro acesso.
        form = ConfiguracaoAgendaForm(
            initial={
                "nome_exibicao": professor.nome_exibicao,
                "dias": [],
                "horarios": [],
            }
        )

    # Exibe a página de configuração inicial.
    return render(
        request,
        "account/configuracao_inicial.html",
        {
            "form": form,
        },
    )


# Decide para onde o usuário deve ir depois do login.
@login_required
def pos_login(request):

    # Recupera ou cria o cadastro do professor.
    professor, _ = Professor.objects.get_or_create(
        usuario=request.user
    )

    # Quem ainda não configurou a agenda vai para a configuração inicial.
    if not professor.agenda_configurada:
        return redirect("configuracao_inicial")

    # Quem já configurou segue para o painel.
    return redirect("painel")


# Página de configurações da conta e da agenda.
@login_required
def configuracoes(request):

    # Recupera ou cria o cadastro do professor.
    professor, _ = Professor.objects.get_or_create(
        usuario=request.user
    )

    # Recupera a agenda principal do professor.
    agenda = obter_agenda_principal(professor)

    # Prepara o formulário de exclusão da conta.
    form_exclusao = ExclusaoContaForm(
        professor=professor
    )

    # Busca somente os horários da agenda principal.
    disponibilidades = (
        DisponibilidadeProfessor.objects.filter(
            professor=professor,
            agenda=agenda,
        ).order_by("dia_semana", "horario")
    )

    # Recupera os dias que já estão configurados.
    dias = sorted(
        set(
            disponibilidade.dia_semana
            for disponibilidade in disponibilidades
        )
    )

    # Recupera os horários que já estão configurados.
    horarios = sorted(
        set(
            disponibilidade.horario
            for disponibilidade in disponibilidades
        )
    )

    # Verifica se o professor enviou alterações.
    if request.method == "POST":
        form = ConfiguracaoAgendaForm(request.POST)

        # Salva somente se o formulário estiver válido.
        if form.is_valid():

            # Mantém as alterações protegidas por uma transação.
            with transaction.atomic():

                # Atualiza o nome de exibição.
                professor.nome_exibicao = (
                    form.cleaned_data["nome_exibicao"]
                )
                professor.save()

                # Atualiza os horários sem recriar os que continuam iguais.
                salvar_disponibilidades(
                    professor,
                    agenda,
                    form.cleaned_data["dias"],
                    form.cleaned_data["horarios"],
                )

            # Retorna às configurações após salvar.
            return redirect("configuracoes")

    else:
        # Converte os números dos dias de volta para os nomes do formulário.
        nomes_dias = {
            0: "segunda",
            1: "terca",
            2: "quarta",
            3: "quinta",
            4: "sexta",
            5: "sabado",
            6: "domingo",
        }

        # Prepara os dias já selecionados.
        dias_iniciais = [
            nomes_dias[dia]
            for dia in dias
        ]

        # Prepara os horários no formato esperado pelo formulário.
        horarios_iniciais = [
            {
                "horario": horario.strftime("%H:%M")
            }
            for horario in horarios
        ]

        # Preenche o formulário com as configurações atuais.
        form = ConfiguracaoAgendaForm(
            initial={
                "nome_exibicao": professor.nome_exibicao,
                "dias": dias_iniciais,
                "horarios": horarios_iniciais,
            }
        )

    # Exibe a página de configurações.
    return render(
        request,
        "account/configuracoes.html",
        {
            "form": form,
            "professor": professor,
            "form_exclusao": form_exclusao,
        },
    )


# Permite que o professor exclua sua própria conta.
@login_required
def excluir_conta(request):

    # Recupera o cadastro do professor autenticado.
    professor = request.user.professor

    # Verifica se o formulário foi enviado.
    if request.method == "POST":

        # Valida os dados de confirmação.
        form = ExclusaoContaForm(
            request.POST,
            professor=professor,
        )

        # Exclui a conta somente se a confirmação estiver correta.
        if form.is_valid():

            # Guarda o usuário antes de encerrar a sessão.
            usuario = request.user

            # Encerra a sessão atual.
            logout(request)

            # Exclui o usuário e os dados relacionados conforme os modelos.
            usuario.delete()

            # Redireciona para a página inicial.
            return redirect("index")

    else:
        # Exibe o formulário vazio de confirmação.
        form = ExclusaoContaForm(
            professor=professor,
        )

    # Se a confirmação não for válida, retorna às configurações.
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
