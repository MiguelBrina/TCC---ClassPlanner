
from django.urls import path

from . import views


urlpatterns = [

    # Página inicial.
    path(
        "",
        views.index,
        name="index",
    ),

    # Agenda semanal.
    path(
        "painel/",
        views.painel,
        name="painel",
    ),

    # Disciplinas.
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

    # Temas.
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

    # Conteúdos.
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

    # Alunos.
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
    path(
        "alunos/<int:aluno_id>/excluir/",
        views.excluir_aluno,
        name="excluir_aluno",
    ),

    # Matrículas.
    path(
        "alunos/<int:aluno_id>/matricular/",
        views.matricular_aluno,
        name="matricular_aluno",
    ),
    path(
        "alunos/<int:aluno_id>/matriculas/<int:matricula_id>/excluir/",
        views.excluir_matricula,
        name="excluir_matricula",
    ),

    # Diário de bordo.
    path(
        "alunos/<int:aluno_id>/matriculas/<int:matricula_id>/diario/",
        views.diario_aluno,
        name="diario_aluno",
    ),

]
