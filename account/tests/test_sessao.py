
import pytest

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from urllib.parse import parse_qs, urlsplit

from account.models import Professor


User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def professor_user():
    usuario = User.objects.create_user(
        username="professor_sessao",
        email="sessao@example.com",
        password="SenhaForte#123",
    )

    Professor.objects.get_or_create(
        usuario=usuario,
    )

    return usuario


def test_sessao_permanece_ativa_entre_requisicoes(
    client,
    professor_user,
):
    client.force_login(professor_user)

    resposta_1 = client.get(reverse("pos_login"))

    assert resposta_1.status_code == 302
    assert resposta_1.url == reverse("configuracao_inicial")

    resposta_2 = client.get(reverse("configuracao_inicial"))

    assert resposta_2.status_code == 200
    assert client.session.get("_auth_user_id") == str(
        professor_user.pk
    )


def test_logout_limpa_sessao(
    client,
    professor_user,
):
    client.force_login(professor_user)

    resposta = client.post(reverse("logout"))

    assert resposta.status_code == 302
    assert resposta.url == reverse("index")
    assert "_auth_user_id" not in client.session

    resposta_painel = client.get(reverse("painel"))

    assert resposta_painel.status_code == 302

    caminho = urlsplit(resposta_painel.url).path
    assert caminho == reverse("login")


def test_visitante_e_redirecionado_para_login_personalizado(
    client,
):
    resposta = client.get(reverse("painel"))

    assert resposta.status_code == 302

    partes_url = urlsplit(resposta.url)

    assert partes_url.path == reverse("login")
    assert parse_qs(partes_url.query).get("next") == [
        reverse("painel")
    ]


def test_sessao_nao_e_compartilhada_entre_clientes(
    professor_user,
):
    cliente_autenticado = Client()
    cliente_anonimo = Client()

    cliente_autenticado.force_login(professor_user)

    resposta_autenticado = cliente_autenticado.get(
        reverse("pos_login")
    )

    resposta_anonimo = cliente_anonimo.get(
        reverse("painel")
    )

    assert resposta_autenticado.status_code == 302
    assert resposta_anonimo.status_code == 302

    assert (
        cliente_autenticado.session.get("_auth_user_id")
        == str(professor_user.pk)
    )

    assert "_auth_user_id" not in cliente_anonimo.session

    assert urlsplit(resposta_anonimo.url).path == reverse("login")
