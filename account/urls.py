from allauth.account.views import SignupView
from django.contrib.auth import views as views_autenticacao
from django.urls import path

from . import views


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

    path(
        "esqueci-senha/",
        views_autenticacao.PasswordResetView.as_view(
            template_name="account/esqueci_senha.html",
            email_template_name="account/email_redefinicao.txt",
            html_email_template_name="account/email_redefinicao.html",
            success_url="/senha-enviada/",
        ),
        name="password_reset",
    ),

    path(
        "senha-enviada/",
        views_autenticacao.PasswordResetDoneView.as_view(
            template_name="account/senha_enviada.html"
        ),
        name="password_reset_done",
    ),

    path(
        "redefinir-senha/<uidb64>/<token>/",
        views_autenticacao.PasswordResetConfirmView.as_view(
            template_name="account/redefinir_senha.html",
            success_url="/senha-redefinida/",
        ),
        name="password_reset_confirm",
    ),

    path(
        "senha-redefinida/",
        views_autenticacao.PasswordResetCompleteView.as_view(
            template_name="account/senha_redefinida.html"
        ),
        name="password_reset_complete",
    ),

    path(
        "configuracao-inicial/",
        views.configuracao_inicial,
        name="configuracao_inicial",
    ),

    path(
        "pos-login/",
        views.pos_login,
        name="pos_login",
    ),

    path(
        "configuracoes/",
        views.configuracoes,
        name="configuracoes",
    ),
    path(
    "excluir-conta/",
    views.excluir_conta,
    name="excluir_conta",
   ),
]