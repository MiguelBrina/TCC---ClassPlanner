from django.shortcuts import render

def index(request):
    return render(request, "index.html")

def painel(request):
    return render(request, "core/painel.html")
