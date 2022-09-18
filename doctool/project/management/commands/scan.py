from django.core.management.base import BaseCommand, CommandError
from pathlib import Path

# from .models import Question as Poll
from django.core import management
from project.renderer import cli_render_all


class Command(BaseCommand):
    help = 'Scan the directory for project files'

    def add_arguments(self, parser):
        parser.add_argument('paths', nargs='+', type=Path)

    # def handle(self, *args, **options):
    #     for poll_id in options['poll_ids']:
    #         try:
    #             poll = Poll.objects.get(pk=poll_id)
    #         except Poll.DoesNotExist:
    #             raise CommandError('Poll "%s" does not exist' % poll_id)

    #         poll.opened = False
    #         poll.save()

    #         self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
    def handle(self, *args, **options):
        # o = options['directory']
        self.stdout.write(self.style.SUCCESS(f'Scan'))
        cli_render_all(*args, **options)
        # management.call_command("runserver")
