from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = "account"
    label= "conta"

    def ready(self):
        print("ACCOUNT APP: carregando signals")
        from . import signals
