from django.apps import AppConfig


class DatasetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datasets'
    verbose_name = 'Dataset Management'

    def ready(self):
        """
        Import signals when app is ready.
        """
        import datasets.signals  # noqa
