from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.urls import path

from two_factor.urls import urlpatterns as tf_urls
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

from derbylane.views import (
    FrontPage,
    ProfileView,
    ScanView,
    AnalysisView,
    load_charts,
    load_bets,
    make_bet,
    logout_view,
)

def buildURL(object_name):
    return (
        r'^%s/'
        r'(?P<verb>[a-z_]+)'
        r'(?:\/(?P<obj_id>[0-9A-Za-z_.@-]+))?'
        r'(?:\/(?P<action>[a-z_]+))?/$' % object_name)

urlpatterns = [
    url(r'', include(tf_urls)),
    url(
        r'^$',
        FrontPage.as_view(),
        name='frontpage'),
    url(
        r'^scans/$',
        ScanView.as_view(),
        name='scans'),
    url(
        r'^analysis/$',
        AnalysisView.as_view(),
        name='analysis'),
    url(
        r'^profile/$',
        ProfileView.as_view(),
        name='profile'),
    path('', include(tf_twilio_urls)),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'logout/$', logout_view, name='logout'),
    url(r'load_charts/$', load_charts, name='load_charts'),
    url(r'load_bets/$', load_bets, name='load_bets'),
    url(r'make_bet/$', make_bet, name='make_bet'),
    url(r'password_reset_form/', auth_views.PasswordResetView.as_view(), name ='password_reset'),
]
