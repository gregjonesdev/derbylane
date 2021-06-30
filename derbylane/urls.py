from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.urls import path

from two_factor.urls import urlpatterns as tf_urls
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

from derbylane.views import (
    Welcome,
    FrontPage,
    ProfileView,
    ScanView,
    DownloadsView,
    UploadsView,
    load_charts,
    load_bets,
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
        Welcome.as_view(),
        name='welcome'),
    url(
        r'^frontpage/$',
        FrontPage.as_view(),
        name='frontpage'),
    url(
        r'^scans/$',
        ScanView.as_view(),
        name='scans'),
    url(
        r'^downloads/$',
        DownloadsView.as_view(),
        name='downloads'),
    url(
        r'^uploads/$',
        UploadsView.as_view(),
        name='uploads'),
    url(
        r'^profile/$',
        ProfileView.as_view(),
        name='profile'),
    path('', include(tf_twilio_urls)),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'logout/$', logout_view, name='logout'),
    url(r'load_charts/$', load_charts, name='load_charts'),
    url(r'load_bets/$', load_bets, name='load_bets'),
    url(r'password_reset_form/', auth_views.PasswordResetView.as_view(), name ='password_reset'),
]

# app_name='registration'
# urlpatterns = [
#     path('registration/', include('django.contrib.auth.urls')),
# ]
