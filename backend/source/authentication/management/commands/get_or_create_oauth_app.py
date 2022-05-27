import logging

from django.core.management import BaseCommand
from oauth2_provider.models import Application

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ensures that an OAuth application with the specified client_id exists. ' \
           'If the app does not exist, it is created.'

    def handle(self, *args, **options):
        app, is_new = Application.objects.get_or_create(
            client_id=options['client_id'],
            defaults={
                'authorization_grant_type': 'authorization-code',
                'client_type': 'public',
                'name': options['name'],
                'redirect_uris': options['redirect_uri'],
            })
        if is_new:
            logger.info(f"New OAuth application created for client_id {options['client_id']}")
        else:
            logger.info(f"There is already an OAuth application with client_id {options['client_id']}")

    def add_arguments(self, parser):
        parser.add_argument(
            'client_id',
            type=str,
            help='The client_id to check',
        )
        parser.add_argument(
            'redirect_uri',
            type=str,
            help='The expected redirect_uri',
        )
        parser.add_argument(
            'name',
            type=str,
            help='The app name to use if the app must be created',
        )
