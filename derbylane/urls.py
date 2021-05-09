from django.conf.urls import url
# from two_factor.urls import urlpatterns as tf_urls

from derbylane.views import (
    Welcome,
)

def buildURL(object_name):
    return (
        r'^%s/'
        r'(?P<verb>[a-z_]+)'
        r'(?:\/(?P<obj_id>[0-9A-Za-z_.@-]+))?'
        r'(?:\/(?P<action>[a-z_]+))?/$' % object_name)

urlpatterns = [
    # url(r'', include(tf_urls)),
    url(
        r'^$',
        Welcome.as_view(),
        name='welcome'),
]
