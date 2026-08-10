from django.shortcuts import render
from  .models import Aluno

def lista_alunos(request):
   
 
   alunos = Aluno.objects.all()    

   return render(request,
          "alunos/lista.html",
          {"alunos": alunos}
            )