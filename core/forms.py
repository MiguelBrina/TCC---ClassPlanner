from django import forms

from .models import Disciplina, Tema

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ["nome"]

class TemaForm(forms.ModelForm):
    class Meta:
        model = Tema
        fields = ["nome"]
