from django.apps import AppConfig


class TexasApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'texas_api'

    def ready(self):
        import texas.sio_events
