from django.apps import AppConfig


class PreferencesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "preferences"
    verbose_name = "好み・ルール"

    def ready(self):
        import preferences.signals  # noqa
