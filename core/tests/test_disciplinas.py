import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from account.models import Professor
from core.models import Disciplina

@pytest.mark.django_db
def test_criar_disciplina(client):
    user, _ = User.objects.get_or_create(username="prof_teste")
    user.set_password("123")
    user.save()
    
    professor, _ = Professor.objects.get_or_create(usuario=user)
    
    client.force_login(user)
    
    url = reverse("lista_disciplinas")
    
    dados = {
        "nome": "Bateria"
    }
    
    resposta = client.post(url, dados)
    
    assert resposta.status_code == 302
    assert Disciplina.objects.count() == 1
    assert Disciplina.objects.first().nome == "Bateria"