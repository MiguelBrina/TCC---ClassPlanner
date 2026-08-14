from django.shortcuts import render

def login(request):
    return render(request, "account/login.html")

def cadastro(request):
    return render(request, "account/cadastro.html")

def esqueci_senha(request):
    return render(request, "account/esqueci_senha.html")

def redefinir_senha(request):
    return render(request, "account/redefinir_senha.html")
