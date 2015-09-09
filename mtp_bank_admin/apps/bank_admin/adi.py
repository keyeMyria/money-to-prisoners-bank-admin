from datetime import datetime
from collections import defaultdict
from decimal import Decimal

from django.conf import settings
from openpyxl import load_workbook, styles
from openpyxl.writer.excel import save_virtual_workbook
from moj_auth import api_client

from . import adi_config as config
from .types import PaymentType, RecordType
from .exceptions import EmptyFileError


class AdiJournal(object):

    STYLE_TYPES = {
        'fill': styles.PatternFill,
        'border': styles.Border,
        'font': styles.Font,
        'alignment': styles.Alignment
    }

    def __init__(self, *args, **kwargs):
        self.wb = load_workbook(settings.ADI_TEMPLATE_FILEPATH)
        self.journal_ws = self.wb.get_sheet_by_name(config.ADI_JOURNAL_SHEET)

        self.current_row = config.ADI_JOURNAL_START_ROW

    def _next_row(self, increment=1):
        self.current_row += increment

    def _set_field(self, field, value, style=None, extra_style=None):
        cell = '%s%s' % (config.ADI_JOURNAL_FIELDS[field]['column'],
                         self.current_row)
        self.journal_ws[cell] = value

        if not style:
            style = defaultdict(dict)
            style.update(config.ADI_JOURNAL_FIELDS[field]['style'])

        if extra_style:
            for key in extra_style:
                style[key].update(extra_style[key])

        for key in style:
            self.journal_ws[cell].__setattr__(
                key,
                self.STYLE_TYPES[key](**style[key])
            )
        return self.journal_ws[cell]

    def _add_column_sum(self, field):
        self._set_field(
            field,
            ('=SUM(%(column)s%(start)s:%(column)s%(end)s)'
                % {
                    'column': config.ADI_JOURNAL_FIELDS[field]['column'],
                    'start': config.ADI_JOURNAL_START_ROW,
                    'end': self.current_row - 1
                })
        )

    def _lookup(self, field, payment_type, record_type, context={}):
        try:
            value_dict = config.ADI_JOURNAL_FIELDS[field]['value']
            value = value_dict[payment_type.name][record_type.name]
            if value:
                return value.format(**context)
        except KeyError:
            pass  # no static value
        return None

    def _finish_journal(self):
        for field in config.ADI_JOURNAL_FIELDS:
            self._set_field(field, '', extra_style=config.ADI_FINAL_ROW_STYLE)

        self._add_column_sum('debit')
        self._add_column_sum('credit')

        bold = {'font': {'bold': True}, 'alignment': {'horizontal': 'left'}}

        self._next_row(increment=3)
        self._set_field('description', 'UPLOADED BY:', style=bold)

        self._next_row(increment=3)
        self._set_field('description', 'CHECKED BY:', style=bold)

        self._next_row(increment=3)
        self._set_field('description', 'POSTED BY:', style=bold)

    def add_payment_row(self, amount, payment_type, record_type, **kwargs):
        for field in config.ADI_JOURNAL_FIELDS:
            static_value = self._lookup(field, payment_type, record_type,
                                        context=kwargs)
            self._set_field(field, static_value)

        if record_type == RecordType.debit:
            self._set_field('debit', float(amount))
        elif record_type == RecordType.credit:
            self._set_field('credit', float(amount))

        self._next_row()

    def create_file(self):
        self._finish_journal()

        today = datetime.now()
        self.journal_ws[config.ADI_DATE_FIELD] = today.strftime('%d/%m/%Y')
        return (today.strftime(settings.OUTPUT_FILENAME),
                save_virtual_workbook(self.wb))


def generate_adi_payment_file(request):
    journal = AdiJournal()

    client = api_client.get_connection(request)
    new_transactions = client.bank_admin.transactions.get(status='credited')

    if len(new_transactions) == 0:
        raise EmptyFileError()

    today = datetime.now().strftime('%d/%m/%Y')
    prison_payments = defaultdict(list)
    for transaction in new_transactions:
        prison_payments[transaction['prison']['nomis_id']].append(transaction)

    # do payments
    for _, transaction_list in prison_payments.items():
        total_credit = sum([Decimal(t['amount']) for t in transaction_list
                            if t['credited']])
        for transaction in transaction_list:
            journal.add_payment_row(
                transaction['amount'], PaymentType.payment, RecordType.debit,
                unique_id=1
            )
        journal.add_payment_row(
            total_credit, PaymentType.payment, RecordType.credit,
            prison_id=transaction_list[0]['prison']['nomis_id'],
            prison_name=transaction_list[0]['prison']['name'],
            date=today
        )

    return journal.create_file()


def generate_adi_refund_file(request):
    journal = AdiJournal()

    client = api_client.get_connection(request)
    refunds = client.bank_admin.transactions.get(status='refunded')

    if len(refunds) == 0:
        raise EmptyFileError()

    today = datetime.now().strftime('%d/%m/%Y')

    # do refunds
    refund_total = sum([Decimal(t['amount']) for t in refunds])
    for refund in refunds:
        journal.add_payment_row(
            refund['amount'], PaymentType.refund, RecordType.debit,
            unique_id=1
        )
    journal.add_payment_row(refund_total, PaymentType.refunded, RecordType.debit,
                            date=today)

    return journal.create_file()
