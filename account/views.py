from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import Professor


def pagina_login(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":

        email = request.POST["email"]
        senha = request.POST["senha"]

        usuario = authenticate(
            request,
            username=email,
            password=senha
        )

        if usuario is not None:
            login(request, usuario)
            return redirect("/")

        return render(
            request,
            "account/login.html",
            {
                "erro": "E-mail ou senha inválidos."
            }
        )

    return render(
        request,
        "account/login.html"
    )


def cadastro(request):

    if request.user.is_authenticated:   
        return redirect("/")
    
    if request.method == "POST":

        nome = request.POST["nome"]
        email = request.POST["email"]
        senha = request.POST["senha"]
        confirmar_senha = request.POST["confirmar_senha"]

        if senha != confirmar_senha:
            return render(
                request,
                "account/cadastro.html",
                {"erro": "As senhas não coincidem."}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "account/cadastro.html",
                {"erro": "Este e-mail já está cadastrado."}
            )

        usuario = User.objects.create_user(
            username=email,
            email=email,
            password=senha,
            first_name=nome
        )

        Professor.objects.create(
            usuario=usuario
        )

        usuario_autenticado = authenticate(
            request,
            username=email,
            password=senha
        )

        if usuario_autenticado is not None:
            login(request, usuario_autenticado)

        return redirect("/")

    return render(
        request,
        "account/cadastro.html"
    )


def esqueci_senha(request):
    return render(request, "account/esqueci_senha.html")


def redefinir_senha(request):
    return render(request, "account/redefinir_senha.html")

def sair(request):
    if request.method == "POST":
        logout(request)

    return redirect("/")