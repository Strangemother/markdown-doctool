from django.apps import AppConfig
from django.core import management
from django.conf import settings


class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'

    def ready(self):
        # importing model classes
        if settings.MEMORY:
            management.call_command("migrate")
        # if settings.PRECACHE_MEMORY:
        #     management.call_command("migrate", '--database', 'precache')

        # management.call_command("runserver")
