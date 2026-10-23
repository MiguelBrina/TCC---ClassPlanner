
import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from urllib.parse import urlsplit

from account.models import Professor


User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def csrf_client():
    return Client(enforce_csrf_checks=True)


@pytest.fixture
def professor_user():
    usuario = User.objects.create_user(
        username="professor_csrf",
        email="csrf@example.com",
        password="SenhaForte#123",
    )

    Professor.objects.get_or_create(
        usuario=usuario,
    )

    return usuario


def dados_agenda_validos():
    return {
        "nome_exibicao": "Professor Teste",
        "dias": '["segunda"]',
        "horarios": '[{"horario": "09:00"}]',
    }


def obter_token_csrf(client, professor_user):
    client.force_login(professor_user)

    host_codespace = urlsplit(settings.SITE_URL).netloc

    resposta = client.get(
        reverse("configuracao_inicial"),
        secure=True,
        HTTP_HOST=host_codespace,
    )

    assert resposta.status_code == 200
    assert "csrftoken" in client.cookies

    return client.cookies["csrftoken"].value


def test_formulario_emite_token_csrf(
    csrf_client,
    professor_user,
):
    token = obter_token_csrf(
        csrf_client,
        professor_user,
    )

    resposta = csrf_client.get(
        reverse("configuracao_inicial"),
        secure=True,
        HTTP_HOST=urlsplit(settings.SITE_URL).netloc,
    )

    assert resposta.status_code == 200
    assert b'name="csrfmiddlewaretoken"' in resposta.content
    assert token


def test_post_sem_token_csrf_retorna_403(
    csrf_client,
    professor_user,
):
    csrf_client.force_login(professor_user)

    resposta = csrf_client.post(
        reverse("configuracao_inicial"),
        dados_agenda_validos(),
    )

    assert resposta.status_code == 403


def test_post_com_token_e_origem_local_confiavel(
    csrf_client,
    professor_user,
):
    token = obter_token_csrf(
        csrf_client,
        professor_user,
    )

    host_codespace = urlsplit(settings.SITE_URL).netloc

    resposta = csrf_client.post(
        reverse("configuracao_inicial"),
        dados_agenda_validos(),
        secure=True,
        HTTP_HOST=host_codespace,
        HTTP_ORIGIN="https://localhost:8000",
        HTTP_X_CSRFTOKEN=token,
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse("painel")


def test_post_com_origem_nao_confiavel_retorna_403(
    csrf_client,
    professor_user,
):
    token = obter_token_csrf(
        csrf_client,
        professor_user,
    )

    host_codespace = urlsplit(settings.SITE_URL).netloc

    resposta = csrf_client.post(
        reverse("configuracao_inicial"),
        dados_agenda_validos(),
        secure=True,
        HTTP_HOST=host_codespace,
        HTTP_ORIGIN="https://malicioso.example",
        HTTP_X_CSRFTOKEN=token,
    )

    assert resposta.status_code == 403
