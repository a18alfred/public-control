from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    # Зарегистрируем сигналы
    def ready(self):
        import accounts.signals
