from django.core.management import BaseCommand


class BaseSourceProcessingCommand(BaseCommand):
    source_class = None

    def handle(self, *args, **options):
        self.source_class.objects.process()
