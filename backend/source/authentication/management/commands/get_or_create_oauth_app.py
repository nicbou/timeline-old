import logging
import secrets
import string

from django.core.management import BaseCommand
from oauth2_provider.models import Application

logger = logging.getLogger(__name__)


def generate_random_string(length):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


class Command(BaseCommand):
    help = 'Ensures that an OAuth application with the specified client_id exists. ' \
           'If the app does not exist, it is created.'

    def handle(self, *args, **options):
        app, is_new = Application.objects.get_or_create(
            client_id=options['client_id'] or generate_random_string(20),
            defaults={
                'name': options['name'],
                'client_secret': options['client_secret'] or generate_random_string(20),
                'client_type': options['client_type'],
                'redirect_uris': options['redirect_uri'] or '',
                'authorization_grant_type': options['authorization_grant'],
            })
        if is_new:
            logger.info(f"New OAuth application created for client_id {options['client_id']}")
        else:
            logger.info(f"There is already an OAuth application with client_id {options['client_id']}")

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str)
        parser.add_argument('--client-id', type=str)
        parser.add_argument('--client-type', type=str)
        parser.add_argument('--client-secret', type=str)
        parser.add_argument('--redirect-uri', type=str)
        parser.add_argument('--authorization-grant', type=str)
