from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = "account"
    label= "conta"

    def ready(self):
        from . import signals
