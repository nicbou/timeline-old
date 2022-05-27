import logging
import sys

from django.core.management import BaseCommand, CommandError
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ensures that the application has at least one user'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.all().count() == 0:
            logger.error('Application has no users. You will not be able to login. '
                         'Create a user with scripts/timeline-create-user.sh')
            sys.exit(1)