from django.apps import AppConfig
from . import processors

class MarkdownProcessorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'markdown_processor'

    # def ready(self):
