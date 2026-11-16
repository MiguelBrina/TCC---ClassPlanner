from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.index,
        name="index",
    ),

    path(
        "painel/",
        views.painel,
        name="painel",
    ),

    path(
        "disciplinas/",
        views.lista_disciplinas,
        name="lista_disciplinas",
    ),

    path(
        "disciplinas/<int:disciplina_id>/temas/",
        views.lista_temas,
        name="lista_temas",
    ),

    path(
        "temas/<int:tema_id>/conteudos/",
        views.lista_conteudos,
        name="lista_conteudos",
    ),

    path(
        "disciplinas/<int:pk>/editar/",
        views.editar_disciplina,
        name="editar_disciplina",
    ),

    path(
        "disciplinas/<int:pk>/excluir/",
        views.excluir_disciplina,
        name="excluir_disciplina",
    ),

    path(
        "temas/<int:pk>/editar/",
        views.editar_tema,
        name="editar_tema",
    ),

    path(
        "temas/<int:pk>/excluir/",
        views.excluir_tema,
        name="excluir_tema",
    ),

    path(
        "conteudos/<int:pk>/editar/",
        views.editar_conteudo,
        name="editar_conteudo",
    ),

    path(
        "conteudos/<int:pk>/excluir/",
        views.excluir_conteudo,
        name="excluir_conteudo",
    ),
        # Alunos
    path(
        "alunos/",
        views.lista_alunos,
        name="lista_alunos",
    ),
    path(
        "alunos/cadastrar/",
        views.cadastrar_aluno,
        name="cadastrar_aluno",
    ),
    path(
        "alunos/<int:aluno_id>/",
        views.detalhe_aluno,
        name="detalhe_aluno",
    ),
    path(
        "alunos/<int:aluno_id>/editar/",
        views.editar_aluno,
        name="editar_aluno",
    ),

    # Matrícula não aparece como uma área independente do sistema.
    # É uma ação iniciada a partir do detalhe do aluno.
    path(
        "alunos/<int:aluno_id>/matricular/",
        views.matricular_aluno,
        name="matricular_aluno",
    ),

    # Diário associado a um aluno e a uma matrícula específica.
    path(
        "alunos/<int:aluno_id>/matriculas/<int:matricula_id>/diario/",
        views.diario_aluno,
        name="diario_aluno",
    ),
]