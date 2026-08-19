from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.pagina_login, name="login"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("esqueci-senha/", views.esqueci_senha, name="esqueci_senha"),
    path("redefinir-senha/", views.redefinir_senha, name="redefinir_senha"),
    path("logout/", views.sair, name="logout"),
]