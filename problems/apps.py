from django.apps import AppConfig


class ProblemsConfig(AppConfig):
    name = 'problems'

    # Зарегистрируем сигналы
    def ready(self):
        import problems.signals
