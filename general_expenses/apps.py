from django.apps import AppConfig


class GeneralExpensesConfig(AppConfig):
    name = 'general_expenses'

    def ready(self):
        import general_expenses.signals
