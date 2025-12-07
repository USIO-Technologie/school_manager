from django.apps import AppConfig


class AppProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_profile'
    verbose_name = 'Profile Management'
    
    def ready(self):
        """
        Méthode appelée lorsque l'application est prête.
        Enregistre les signaux.
        """
        import app_profile.signals  # noqa