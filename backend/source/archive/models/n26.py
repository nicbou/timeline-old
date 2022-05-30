import codecs
import csv
import logging
from typing import Generator
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
            account_iban = None

            # Loop once to find account owner's iban
            for line in csv.DictReader(codecs.iterdecode(csv_file.open('rb'), 'utf-8'), delimiter=',', quotechar='"'):
                if line['Transaction type'] in income_types and line['Account number']:
                    account_iban = line['Account number']
                    break

            for line in csv.DictReader(codecs.iterdecode(csv_file.open('rb'), 'utf-8'), delimiter=',', quotechar='"'):
                schema = 'finance.income' if line['Transaction type'] in income_types else 'finance.expense'

                first_party = {
                    'name': None,
                    'amount': str(Decimal(line['Amount (EUR)']).copy_abs()),
                    'currency': default_currency,
                }
                if account_iban:
                    first_party['iban'] = account_iban

                third_party = {
                    'name': line['Payee'],
                    'amount': str(Decimal(line['Amount (Foreign Currency)'] or line['Amount (EUR)']).copy_abs()),
                    'currency': line['Type Foreign Currency'] or default_currency,
                }
                if line['Account number']:
                    third_party['iban'] = line['Account number']

                # The transactions don't have a time. Set it to noon, local timezone
                entry_date = pytz.timezone(default_timezone)\
                    .localize(datetime.strptime(line['Date'], '%Y-%m-%d'))\
                    .replace(hour=12)\
                    .astimezone(pytz.UTC)

                yield Entry(
                    schema=schema,
                    source=self.entry_source,
                    title=line['Transaction type'],
                    description='' if line['Payment reference'] == '-' else line['Payment reference'],
                    extra_attributes={
                        'bank': {'name': 'N26'},
                        'sender': first_party if schema == 'finance.expense' else third_party,
                        'recipient': third_party if schema == 'finance.expense' else first_party,
                    },
                    date_on_timeline=entry_date
                )
