from django.apps import AppConfig


class AccountBalanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "account_balance"

    def ready(self):
        from . import signals
