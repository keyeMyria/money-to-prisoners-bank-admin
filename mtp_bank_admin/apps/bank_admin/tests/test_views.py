import logging

from unittest import mock
from django.test import SimpleTestCase
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from moj_auth.tests.utils import generate_tokens
from moj_auth.exceptions import Unauthorized

from . import get_test_transactions, NO_TRANSACTIONS
from .test_refund import REFUND_TRANSACTIONS
from ..types import PaymentType


class BankAdminViewTestCase(SimpleTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    @mock.patch('moj_auth.backends.api_client')
    def login(self, mock_api_client):
        mock_api_client.authenticate.return_value = {
            'pk': 5,
            'token': generate_tokens(),
            'user_data': {
                'first_name': 'Sam',
                'last_name': 'Hall',
                'username': 'shall'
            }
        }

        response = self.client.post(
            reverse('login'),
            data={'username': 'shall', 'password': 'pass'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)

    def check_login_redirect(self, attempted_url):
        response = self.client.get(attempted_url)
        redirect_url = '%(login_url)s?next=%(attempted_url)s' % \
            {'login_url': reverse('login'),
             'attempted_url': attempted_url}
        self.assertRedirects(response, redirect_url)


class DashboardButtonVisibilityTestCase(BankAdminViewTestCase):

    @mock.patch('moj_auth.backends.api_client')
    def test_can_see_refund_download_with_perm(self, mock_api_client):
        mock_api_client.authenticate.return_value = {
            'pk': 5,
            'token': generate_tokens(),
            'user_data': {
                'first_name': 'Sam',
                'last_name': 'Hall',
                'username': 'shall',
                'permissions': ['transaction.view_bank_details_transaction']
            }
        }

        response = self.client.post(
            reverse('login'),
            data={'username': 'shall', 'password': 'pass'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('bank_admin:download_refund_file'))

    @mock.patch('moj_auth.backends.api_client')
    def test_cannot_see_refund_download_without_perm(self, mock_api_client):
        mock_api_client.authenticate.return_value = {
            'pk': 5,
            'token': generate_tokens(),
            'user_data': {
                'first_name': 'Sam',
                'last_name': 'Hall',
                'username': 'shall',
                'permissions': []
            }
        }

        response = self.client.post(
            reverse('login'),
            data={'username': 'shall', 'password': 'pass'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('bank_admin:download_refund_file'))


class DownloadRefundFileViewTestCase(BankAdminViewTestCase):

    def test_dashboard_requires_login(self):
        self.check_login_redirect(reverse('bank_admin:dashboard'))

    def test_download_refund_file_requires_login(self):
        self.check_login_redirect(reverse('bank_admin:download_refund_file'))

    @mock.patch('bank_admin.utils.api_client')
    def test_download_refund_file(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.side_effect = REFUND_TRANSACTIONS

        response = self.client.get(reverse('bank_admin:download_refund_file'))

        self.assertEqual(200, response.status_code)
        self.assertEqual('text/csv', response['Content-Type'])
        self.assertEqual(
            bytes(('111111,22222222,John Doe,25.68,%(ref)s\r\n' +
                   '999999,33333333,Joe Bloggs,18.72,%(ref)s\r\n')
                  % {'ref': settings.REFUND_REFERENCE}, 'utf8'),
            response.content)


@mock.patch('bank_admin.utils.api_client')
class DownloadRefundFileErrorViewTestCase(BankAdminViewTestCase):

    def test_download_refund_file_general_error_message(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.side_effect = Unauthorized()

        response = self.client.get(reverse('bank_admin:download_refund_file'),
                                   follow=False)

        self.assertRedirects(response, reverse('login'))

    def test_download_refund_file_no_transactions_error_message(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.return_value = NO_TRANSACTIONS

        response = self.client.get(reverse('bank_admin:download_refund_file'),
                                   follow=True)

        self.assertContains(response,
                            _('No new transactions available for refund'),
                            status_code=200)


class DownloadAdiFileViewTestCase(BankAdminViewTestCase):

    def test_dashboard_requires_login(self):
        self.check_login_redirect(reverse('bank_admin:dashboard'))

    def test_download_adi_payment_file_requires_login(self):
        self.check_login_redirect(reverse('bank_admin:download_adi_payment_file'))

    def test_download_adi_refund_file_requires_login(self):
        self.check_login_redirect(reverse('bank_admin:download_adi_refund_file'))

    @mock.patch('bank_admin.utils.api_client')
    def test_download_adi_payment_file(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.return_value = get_test_transactions(PaymentType.payment)

        response = self.client.get(reverse('bank_admin:download_adi_payment_file'))

        self.assertEqual(200, response.status_code)
        self.assertEqual('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', response['Content-Type'])

    @mock.patch('bank_admin.utils.api_client')
    def test_download_adi_refund_file(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.return_value = get_test_transactions(PaymentType.refund)

        response = self.client.get(reverse('bank_admin:download_adi_refund_file'))

        self.assertEqual(200, response.status_code)
        self.assertEqual('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', response['Content-Type'])


@mock.patch('bank_admin.utils.api_client')
class DownloadAdiFileErrorViewTestCase(BankAdminViewTestCase):

    def test_download_adi_payment_file_general_error_message(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.side_effect = Unauthorized()

        response = self.client.get(reverse('bank_admin:download_adi_payment_file'),
                                   follow=False)

        self.assertRedirects(response, reverse('login'))

    def test_download_adi_refund_file_general_error_message(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.side_effect = Unauthorized()

        response = self.client.get(reverse('bank_admin:download_adi_refund_file'),
                                   follow=False)

        self.assertRedirects(response, reverse('login'))

    def test_download_adi_payment_file_no_transactions_error_message(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.return_value = NO_TRANSACTIONS

        response = self.client.get(reverse('bank_admin:download_adi_payment_file'),
                                   follow=True)

        self.assertContains(response,
                            _('No new transactions available for reconciliation'),
                            status_code=200)

    def test_download_adi_refund_file_no_transactions_error_message(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.return_value = NO_TRANSACTIONS

        response = self.client.get(reverse('bank_admin:download_adi_refund_file'),
                                   follow=True)

        self.assertContains(response,
                            _('No new transactions available for reconciliation'),
                            status_code=200)


class DownloadBankStatementViewTestCase(BankAdminViewTestCase):

    def test_download_adi_refund_file_requires_login(self):
        self.check_login_redirect(reverse('bank_admin:download_adi_refund_file'))

    @mock.patch('bank_admin.statement.api_client')
    @mock.patch('bank_admin.utils.api_client')
    def test_download_bank_statement(self, mock_api_client,
                                     mock_stmt_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.return_value = get_test_transactions()

        balance_conn = mock_stmt_api_client.get_connection().batches
        balance_conn.get.return_value = {'results': []}

        response = self.client.get(reverse('bank_admin:download_bank_statement'))

        self.assertEqual(200, response.status_code)
        self.assertEqual('text/plain', response['Content-Type'])


@mock.patch('bank_admin.utils.api_client')
class DownloadBankStatementErrorViewTestCase(BankAdminViewTestCase):

    def test_download_bank_statement_general_error_message(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.side_effect = Unauthorized()

        response = self.client.get(reverse('bank_admin:download_bank_statement'),
                                   follow=False)

        self.assertRedirects(response, reverse('login'))

    def test_download_bank_statement_no_transactions_error_message(self, mock_api_client):
        self.login()

        conn = mock_api_client.get_connection().bank_admin.transactions
        conn.get.return_value = NO_TRANSACTIONS

        response = self.client.get(reverse('bank_admin:download_bank_statement'),
                                   follow=True)

        self.assertContains(response,
                            _('No new transactions available on account'),
                            status_code=200)
