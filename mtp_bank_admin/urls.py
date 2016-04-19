from django.conf.urls import include, url
from django.core.urlresolvers import reverse_lazy

from moj_auth import views
from moj_irat.views import HealthcheckView, PingJsonView

urlpatterns = [
    url(
        r'^login/$', views.login, {
            'template_name': 'mtp_auth/login.html'
        }, name='login'
    ),
    url(
        r'^logout/$', views.logout, {
            'template_name': 'mtp_auth/login.html',
            'next_page': reverse_lazy('login'),
        }, name='logout'
    ),
    url(
        r'^password_change/$', views.password_change, {
            'template_name': 'auth/password_change.html'
        }, name='password_change'
    ),
    url(
        r'^password_change_done/$', views.password_change_done, {
            'template_name': 'auth/password_change_done.html'
        }, name='password_change_done'
    ),
    url(
        r'^reset-password/$', views.reset_password, {
            'template_name': 'auth/reset-password.html',
            'cancel_url': reverse_lazy('bank_admin:dashboard'),
        }, name='reset_password'
    ),
    url(
        r'^reset-password-done/$', views.reset_password_done, {
            'template_name': 'auth/reset-password-done.html',
            'cancel_url': reverse_lazy('bank_admin:dashboard'),
        }, name='reset_password_done'
    ),

    url(r'^', include('bank_admin.urls', namespace='bank_admin',)),
    url(r'^', include('feedback.urls')),

    url(r'^ping.json$', PingJsonView.as_view(
        build_date_key='APP_BUILD_DATE',
        commit_id_key='APP_GIT_COMMIT',
        version_number_key='APP_BUILD_TAG',
    ), name='ping_json'),
    url(r'^healthcheck.json$', HealthcheckView.as_view(), name='healthcheck_json'),
]
