
import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.urls import reverse

from account.models import Professor


User = get_user_model()

pytestmark = pytest.mark.django_db

SENHA_VALIDA = "SenhaForte#123"


@pytest.fixture
def google_social_app():
    site, _ = Site.objects.get_or_create(
        pk=settings.SITE_ID,
        defaults={
            "domain": "testserver",
            "name": "testserver",
        },
    )

    app = SocialApp.objects.create(
        provider="google",
        name="Google Teste",
        client_id="client-id-falso",
        secret="secret-falso",
    )

    app.sites.add(site)

    return app


def criar_usuario_verificado(
    email="professor@example.com",
    username="professor_teste",
):
    usuario = User.objects.create_user(
        username=username,
        email=email,
        password=SENHA_VALIDA,
    )

    EmailAddress.objects.update_or_create(
        user=usuario,
        email=email,
        defaults={
            "primary": True,
            "verified": True,
        },
    )

    Professor.objects.get_or_create(
        usuario=usuario,
    )

    return usuario


def test_pagina_login_carrega_formulario(
    client,
    google_social_app,
):
    resposta = client.get(reverse("login"))

    assert resposta.status_code == 200
    assert b"E-mail" in resposta.content
    assert b'name="username"' in resposta.content
    assert b'name="password"' in resposta.content


def test_login_com_senha_incorreta_nao_autentica(
    client,
    google_social_app,
):
    criar_usuario_verificado()

    resposta = client.post(
        reverse("login"),
        {
            "username": "professor@example.com",
            "password": "senha-errada",
        },
    )

    assert resposta.status_code == 200
    assert resposta.context["form"].errors
    assert not client.session.get("_auth_user_id")


def test_login_com_usuario_inexistente_nao_autentica(
    client,
    google_social_app,
):
    resposta = client.post(
        reverse("login"),
        {
            "username": "inexistente@example.com",
            "password": SENHA_VALIDA,
        },
    )

    assert resposta.status_code == 200
    assert resposta.context["form"].errors
    assert not client.session.get("_auth_user_id")


def test_login_com_email_valido_cria_sessao(
    client,
    google_social_app,
):
    usuario = criar_usuario_verificado()

    resposta = client.post(
        reverse("login"),
        {
            "username": usuario.email,
            "password": SENHA_VALIDA,
        },
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse("pos_login")
    assert client.session.get("_auth_user_id") == str(usuario.pk)


def test_login_respeita_redirecionamento_next(
    client,
    google_social_app,
):
    usuario = criar_usuario_verificado()

    url_login = f"{reverse('login')}?next={reverse('painel')}"

    resposta = client.post(
        url_login,
        {
            "username": usuario.email,
            "password": SENHA_VALIDA,
        },
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse("painel")
    assert client.session.get("_auth_user_id") == str(usuario.pk)
