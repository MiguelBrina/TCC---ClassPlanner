import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from account.models import Professor


User = get_user_model()

pytestmark = pytest.mark.django_db

SENHA_VALIDA = "SenhaForte#123"


def dados_cadastro(**alteracoes):
    dados = {
        "email": "novo@example.com",
        "nome": "Miguel Teste",
        "password1": SENHA_VALIDA,
        "password2": SENHA_VALIDA,
    }

    dados.update(alteracoes)

    return dados


def test_pagina_cadastro_carrega_formulario(client):
    resposta = client.get(reverse("cadastro"))

    assert resposta.status_code == 200
    assert b"Criar conta" in resposta.content
    assert b'name="email"' in resposta.content
    assert b'name="nome"' in resposta.content
    assert b'name="password1"' in resposta.content
    assert b'name="password2"' in resposta.content


def test_cadastro_valido_cria_usuario_e_professor(client):
    resposta = client.post(
        reverse("cadastro"),
        dados_cadastro(),
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse("account_email_verification_sent")

    usuario = User.objects.get(email="novo@example.com")

    assert usuario.first_name == "Miguel Teste"
    assert usuario.check_password(SENHA_VALIDA)

    assert Professor.objects.filter(
        usuario=usuario
    ).count() == 1
    
    assert not client.session.get("_auth_user_id")

def test_senhas_diferentes_impedem_cadastro(client):
    usuarios_antes = User.objects.count()
    professores_antes = Professor.objects.count()

    resposta = client.post(
        reverse("cadastro"),
        dados_cadastro(
            password2="OutraSenha#456",
        ),
    )

    assert resposta.status_code == 200
    assert resposta.context["form"].errors

    assert User.objects.count() == usuarios_antes
    assert Professor.objects.count() == professores_antes


def test_email_invalido_impede_cadastro(client):
    usuarios_antes = User.objects.count()
    professores_antes = Professor.objects.count()

    resposta = client.post(
        reverse("cadastro"),
        dados_cadastro(
            email="email-invalido",
        ),
    )

    assert resposta.status_code == 200
    assert "email" in resposta.context["form"].errors

    assert User.objects.count() == usuarios_antes
    assert Professor.objects.count() == professores_antes


def test_email_duplicado_impede_cadastro(client):
    User.objects.create_user(
        username="usuario_existente",
        email="novo@example.com",
        password=SENHA_VALIDA,
    )

    usuarios_antes = User.objects.count()
    professores_antes = Professor.objects.count()

    resposta = client.post(
        reverse("cadastro"),
        dados_cadastro(),
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse(
        "account_email_verification_sent"
    )

    assert User.objects.count() == usuarios_antes
    assert Professor.objects.count() == professores_antes

def test_senha_fraca_impede_cadastro(client):
    usuarios_antes = User.objects.count()
    professores_antes = Professor.objects.count()

    resposta = client.post(
        reverse("cadastro"),
        dados_cadastro(
            password1="1234567890",
            password2="1234567890",
        ),
    )

    assert resposta.status_code == 200
    assert "password1" in resposta.context["form"].errors

    assert User.objects.count() == usuarios_antes
    assert Professor.objects.count() == professores_antes

def test_cadastro_sem_nome_impede_criacao(client):
    usuarios_antes  = User.objects.count()
    professores_antes = Professor.objects.count()
    
    resposta = client.post(
        reverse("cadastro"),
        dados_cadastro(
            nome = ""
        ),
    )

    assert resposta.status_code == 200
    assert "nome" in resposta.context["form"].errors

    assert User.objects.count() == usuarios_antes
    assert Professor.objects.count() == professores_antes