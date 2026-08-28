from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("painel/", views.painel, name="painel"),
    path("diagnostico-host/",views.diagnostico_host,name="diagnostico_host"),
]