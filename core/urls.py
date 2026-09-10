from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("painel/", views.painel, name="painel"),
    path("disciplinas/",views.lista_disciplinas,name="lista_disciplinas",
),
]
