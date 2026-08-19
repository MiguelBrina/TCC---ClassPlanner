from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def index(request):
    return render(request, "index.html")

def painel(request):
    return render(request, "core/painel.html")

def inicio(request):
    if request.user.is_authenticated:
        return redirect("painel")
    
    return render(request, "index.html")

@login_required
def painel(request):
    return render(request, "core/painel.html")