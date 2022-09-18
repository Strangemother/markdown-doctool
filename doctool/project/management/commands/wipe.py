from django.core.management.base import BaseCommand, CommandError
from pathlib import Path

# from .models import Question as Poll
from project.renderer import cli_render_all
from project import models

class Command(BaseCommand):
    help = 'Destroy all projects and associated files'

    # def add_arguments(self, parser):
    #     parser.add_argument('paths', nargs='+', type=Path)

    def handle(self, *args, **options):
        # o = options['directory']
        v = models.Project.objects.all().delete()
        v2 = models.FileOutput.objects.all().delete()
        v = models.OutputDirectory.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deletes: {v} {v2}'))


