from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.urls import path

from two_factor.urls import urlpatterns as tf_urls
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

from derbylane.views import (
    Welcome,
    FrontPage,
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
    path('', include(tf_twilio_urls)),
    path('accounts/', include('django.contrib.auth.urls')),
]
