from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.urls import path

from two_factor.urls import urlpatterns as tf_urls
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

from derbylane.views import (
    FrontPage,
    ProfileView,
    AnalysisView,
    ResultsView,
    WeatherView,
    PasswordReset,
    load_charts,
    load_bets,
    make_bet,
    make_exotic_bet,
    delete_exotic_bet,
    clear_bets,
    get_bets,
    get_venue_bets,
    logout_view,
    change_password,
)
def buildURL(object_name):
    return (
        r'^%s/'
        r'(?P<verb>[a-z_]+)'
        r'(?:\/(?P<obj_id>[0-9A-Za-z_.@-]+))?'
        r'(?:\/(?P<action>[a-z_]+))?/$' % object_name)

urlpatterns = [
    url(r'', include(tf_urls)),
    url(r'', include('django.contrib.auth.urls')),
    url(
        r'^$',
        FrontPage.as_view(),
        name='frontpage'),
    url(
        r'^results/$',
        ResultsView.as_view(),
        name='results'),
    url(
        r'^weather/$',
        WeatherView.as_view(),
        name='weather'),
    url(
        r'^profile/$',
        ProfileView.as_view(),
        name='profile'),
    url(
        r'^analysis/$',
        AnalysisView.as_view(),
        name='analysis'),
    path('', include(tf_twilio_urls)),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('password_reset_form/', auth_views.PasswordChangeView.as_view(), name='password_reset'),
    # path('login/', auth_views.PasswordChangeView.as_view(), name='login'),
    # url(r'password_reset_form/$', auth_views.PasswordResetView.as_view(), name='password_reset_form'),

    # url(r'logout/$', logout_view, name='logout'),
    url(r'change_password/$', change_password, name='change_password'),
    url(r'load_charts/$', load_charts, name='load_charts'),
    url(r'load_bets/$', load_bets, name='load_bets'),
    url(r'get_bets/$', get_bets, name='get_bets'),
    url(r'get_venue_bets/$', get_venue_bets, name='get_venue_bets'),

    url(r'make_bet/$', make_bet, name='make_bet'),
    url(r'make_exotic_bet/$', make_exotic_bet, name='make_exotic_bet'),
    url(r'delete_exotic_bet/$', delete_exotic_bet, name='delete_exotic_bet'),
    url(r'clear_bet/$', clear_bets, name='clear_bets'),
    url(r'password_reset_form/', auth_views.PasswordResetView.as_view(), name ='password_reset'),
]
