
from django.urls import path
from django.urls import include

urlpatterns = [
    path("", include("alunos.urls")),
    path("disciplinas/", include("disciplinas.urls")),
]
