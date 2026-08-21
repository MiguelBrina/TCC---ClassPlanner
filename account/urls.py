from allauth.account.views import SignupView
from django.urls import path
from django.contrib.auth import views as views_autenticacao


urlpatterns = [
    path(
        "cadastro/",
        SignupView.as_view(
            template_name="account/cadastro.html"
        ),
        name="cadastro",
    ),

    path(
        "login/",
        views_autenticacao.LoginView.as_view(
            template_name="account/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        views_autenticacao.LogoutView.as_view(),
        name="logout",
    ),

    # recuperação depois
    path(
        "esqueci-senha/",
        views_autenticacao.PasswordResetView.as_view(
            template_name="account/esqueci_senha.html",
            email_template_name="account/email_redefinicao.txt",
            success_url="/senha-enviada/",
        ),
    name="esqueci_senha",
    ),

    path(
        "senha-enviada/",
        views_autenticacao.PasswordResetDoneView.as_view(
            template_name="account/senha_enviada.html"
        ),
        name="senha_enviada",
    ),

    path(
        "redefinir-senha/<uidb64>/<token>/",
        views_autenticacao.PasswordResetConfirmView.as_view(
            template_name="account/redefinir_senha.html",
            success_url="/senha-redefinida/",
        ),
    name="redefinir_senha",
    ),

    
]