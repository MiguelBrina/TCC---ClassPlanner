import re

from django.core.exceptions import ValidationError


class ValidadorSenhaForte:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "A senha deve conter pelo menos uma letra maiúscula."
            )

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                "A senha deve conter pelo menos uma letra minúscula."
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                "A senha deve conter pelo menos um número."
            )

        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError(
                "A senha deve conter pelo menos um caractere especial."
            )

    def get_help_text(self):
        return (
            "A senha deve conter pelo menos 10 caracteres, "
            "uma letra maiúscula, uma letra minúscula, "
            "um número e um caractere especial."
        )