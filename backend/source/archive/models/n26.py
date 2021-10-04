import codecs
import csv
import logging
from collections import Generator
from datetime import datetime
from decimal import Decimal

import pytz

from archive.models.base import FileArchive
from timeline.models import Entry

logger = logging.getLogger(__name__)


class N26CsvArchive(FileArchive):
    """
    Reads CSV transaction lists exported by N26
    """
    def extract_entries(self) -> Generator[Entry, None, None]:
        default_currency = 'EUR'
        default_timezone = 'Europe/Berlin'  # TODO: If this thing gets a million users, that assumption could be wrong
        income_types = ('Income', 'Direct Debit Reversal')

        for csv_file in self.get_archive_files():
            for line in csv.DictReader(codecs.iterdecode(csv_file.open('rb'), 'utf-8'), delimiter=',', quotechar='"'):
                schema = 'finance.income' if line['Transaction type'] in income_types else 'finance.expense'

                you = {
                    'currency': default_currency,
                    'amount': Decimal(line['Amount (EUR)']).copy_abs(),
                    'name': None,
                }

                other_party = {
                    'currency': line['Type Foreign Currency'] or default_currency,
                    'amount': Decimal(line['Amount (Foreign Currency)'] or line['Amount (EUR)']).copy_abs(),
                    'name': line['Payee'],
                }

                sender = you if schema == 'finance.expense' else other_party
                recipient = other_party if schema == 'finance.expense' else you

                # The transactions don't have a time. Set it to noon, Berlin time
                entry_date = pytz.timezone(default_timezone)\
                    .localize(datetime.strptime(line['Date'], '%Y-%m-%d'))\
                    .replace(hour=12)\
                    .astimezone(pytz.UTC)

                yield Entry(
                    schema=schema,
                    source=self.entry_source,
                    title=line['Transaction type'],
                    description=line['Payment reference'],
                    extra_attributes={
                        'sender_amount': str(sender['amount']),
                        'sender_currency': sender['currency'],
                        'sender_name': sender['name'],
                        'recipient_amount': str(recipient['amount']),
                        'recipient_currency': recipient['currency'],
                        'recipient_name': recipient['name'],
                    },
                    date_on_timeline=entry_date
                )
