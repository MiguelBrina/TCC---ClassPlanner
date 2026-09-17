from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("painel/", views.painel, name="painel"),
    path("disciplinas/",views.lista_disciplinas,name="lista_disciplinas"),
    path("disciplinas/<int:disciplina_id>/temas/",views.lista_temas, name="lista_temas"),
    path("disciplinas/<disciplina_id>/temas/<int:tema_id>/conteudos/", views.lista_conteudos, name="lista_conteudos"),
    path("temas/<int:tema_id>/conteudos/",views.lista_conteudos,name="lista_conteudos",
),
]
