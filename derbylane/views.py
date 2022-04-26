# import os, fnmatch
from django.utils.timezone import localdate
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
import datetime
from django.shortcuts import redirect
from django.views.generic import View
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from two_factor.views.mixins import OTPRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect


from rawdat.models import (
    Venue,
    Chart,
    CronJob,
    Program,
    Participant,
    Bet,
    StraightBetType,
    Straight_Wager)


class FrontPage(LoginRequiredMixin, View):

    template_name = 'frontpage.html'
    context = {}

    def get(self, request, *args, **kwargs):
        datestring = request.GET.get("date")
        displayed_charts = []
        today = localdate()
        if datestring:
            target_day = datetime.datetime.strptime(datestring, "%Y-%m-%d").date()
        else:
            target_day = today




        if target_day + datetime.timedelta(days=1) < today:
            previous_date = None
            next_date = today.strftime("%Y-%m-%d")
            placed_bets = Bet.objects.all()
            future_bets = placed_bets.filter(
                participant__race__chart__program__date__gt=target_day).order_by(
                "participant__race__chart__program__date")
            past_bets = placed_bets.filter(
                participant__race__chart__program__date__lt=target_day).order_by(
                "-participant__race__chart__program__date")
            if future_bets.count() > 0:
                next_date = future_bets[0].get_date().strftime("%Y-%m-%d")
            else:
                next_date = today.strftime("%Y-%m-%d")
            if past_bets.count() > 0:
                previous_date = past_bets[0].get_date().strftime("%Y-%m-%d")
            else:
                previous_date = None
        else:
            previous_date = (target_day - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            if target_day > today:
                next_date = None
            else:
                next_date = (target_day + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        if target_day < today:
            content_type = "Bets"
        else:
            content_type = "Predictions"

        if target_day.year < today.year:
            date_header = target_day.strftime("%a, %b %-d, %Y")
        else:
            date_header = target_day.strftime("%A, %B %-d")

        displayed_charts = []
        for chart in Chart.objects.filter(program__date=target_day):
             if chart.has_bets():
                 displayed_charts.append(chart)


        self.context["previous"] = previous_date
        self.context["next"] = next_date
        self.context["date_header"] = date_header
        self.context["datestring"] = datestring
        self.context["charts"] = displayed_charts
        self.context["content_type"] = content_type
        return render(request, self.template_name, self.context)



class ProfileView(OTPRequiredMixin, View):

    template_name = 'profile.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

class WeatherView(LoginRequiredMixin, View):

    template_name = 'weather.html'
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["venues"] = Venue.objects.filter(is_focused=True)
        return render(request, self.template_name, self.context)


class ResultsView(LoginRequiredMixin, View):

    template_name = 'results.html'
    context = {}

    def get(self, request, *args, **kwargs):
        try:
            target_date = datetime.datetime.fromisoformat(
                request.GET.get("date"))
        except:
            target_date = localdate()
        bets = Bet.objects.filter(
            participant__race__chart__program__date=target_date).order_by(
                'participant__race__chart', 'participant__race')
        self.context["bets"] = bets
        self.context["day"] = target_date.strftime("%A")
        self.context["date"] = target_date.strftime("%Y-%m-%d")
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        response = redirect('results')
        response['Location'] += '?date={}'.format(
            request.POST.get("date"))
        return response


class PasswordReset(auth_views.PasswordResetView):

    context = {}
    def get(self, request, *args, **kwargs):
        print("hola")
        return render(request, self.template_name, self.context)

def load_charts(request):
    venue = Venue.objects.get(
        code=request.GET.get('venue_code'))
    charts = Chart.objects.filter(
        program__venue=venue,
        program__date=datetime.datetime.now()
    )
    return render(
        request,
        'load_charts.html', {'charts': charts, })

def make_bet(request):
    participant_id = request.GET.get('participant_id')
    participant = Participant.objects.get(
        uuid=participant_id)
    bet_names = [char for char in request.GET.get('bet_types')]
    bet_update = {'W': 0, 'P': 0, 'S': 0}
    for bet_name in bet_names:
        type = StraightBetType.objects.get(name=bet_name)
        try:
            bet = Bet.objects.get(
                participant = participant,
                type = type
            )
        except ObjectDoesNotExist:
            new_bet = Bet(
                participant = participant,
                type = type
            )
            new_bet.set_fields_to_base()
            new_bet.save()
            bet = new_bet
        amount = request.GET.get('amount')
        if int(amount) == 0:
            bet.delete()
        else:
            bet.amount = float(amount)
            bet.save()
            bet_update[bet_name] = bet.amount

    return JsonResponse({
        'bets': bet_update,
        'participant_id': participant_id })

def clear_bets(request):
    participant_id = request.GET.get('participant_id')
    participant = Participant.objects.get(
        uuid=participant_id)
    for bet in Bet.objects.filter(
        participant=participant):
        bet.delete()
    return JsonResponse({
        'participant_id': participant_id })


def load_bets(request):
    try:
        chart = Chart.objects.get(
            uuid=request.GET.get('chart_id'))
    except:
        pass
    if chart:
        wagering = False
        if not localdate() > chart.program.date:
            wagering = True
        url = 'load_bets.html'
        races = chart.race_set.filter(
            grade__value__gt=0)
        return render(
            request,
            url, {
                'races': races,
                'wagering': wagering })

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect("/")
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form,
        'user': request.user
    })


def logout_view(request):
    logout(request)
    response = redirect('/')
    return response
