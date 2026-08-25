from django.urls import path
from . import views


urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("painel/", views.painel, name="painel"),
    path("diagnostico-host/",views.diagnostico_host,name="diagnostico_host"),
]