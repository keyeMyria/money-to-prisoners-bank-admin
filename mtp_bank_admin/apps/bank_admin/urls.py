from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    url(r'^$', login_required(TemplateView.as_view(
        template_name='bank_admin/dashboard.html')),
        name='dashboard'),
    url(r'^refund_pending/download/$', views.download_refund_file,
        name='download_refund_file'),
    url(r'^previously_refunded/download/$', views.download_previous_refund_file,
        name='download_previous_refund_file'),
    url(r'^adi/payment/download/$', views.download_adi_payment_file,
        name='download_adi_payment_file'),
    url(r'^adi/refund/download/$', views.download_adi_refund_file,
        name='download_adi_refund_file'),
    url(r'^bank_statement/download/$', views.download_bank_statement,
        name='download_bank_statement')
]
