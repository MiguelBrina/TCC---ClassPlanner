from django import forms

from .models import Disciplina

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ["nome"]