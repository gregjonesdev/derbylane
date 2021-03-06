
from django.utils.timezone import localdate
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
import datetime
import time

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect
from django.views.generic import View
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from two_factor.views.mixins import OTPRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.http import HttpResponse


from rawdat.models import (
    Venue,
    Chart,
    CronJob,
    Program,
    Participant,
    Bet,
    Race,
    StraightBetType,
    Straight_Wager,
    # Quiniela_Wager,
    Sizzle_Superfecta,
    Straight_Bet,
    )


class FrontPage(LoginRequiredMixin, View):

    template_name = 'frontpage.html'
    context = {}

    def get(self, request, *args, **kwargs):
        datestring = request.GET.get("date")
        displayed_charts = []
        today = datetime.datetime.now().date()
        hour = time.localtime().tm_hour

        chart_sort = "time"
        if hour >= 17:
            chart_sort = "-time"
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

        displayed_charts = []

        # if target_day < today:
        #     content_type = "Bets"
        for chart in Chart.objects.filter(program__date=target_day):
            if chart.has_predictions():
                displayed_charts.append(chart)
        # else:
        #     for chart in Chart.objects.filter(
        #         program__date=target_day).order_by(
        #         chart_sort):
        #         if chart.has_predictions():
        #             displayed_charts.append(chart)

        if target_day.year < today.year:
            date_header = target_day.strftime("%a, %b %-d, %Y")
        else:
            date_header = target_day.strftime("%A, %B %-d")




        self.context["previous"] = previous_date
        self.context["next"] = next_date
        self.context["date_header"] = date_header
        self.context["datestring"] = datestring
        self.context["charts"] = displayed_charts
        return render(request, self.template_name, self.context)


class AnalysisView(LoginRequiredMixin, View):

    template_name = 'analysis.html'
    context = {}

    def get(self, request, *args, **kwargs):
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)

        # first date of smoreg bets: 2022-05-16
        self.context["yesterday"] = yesterday.strftime("%a %b %-d")
        self.context["yesterday_date"] = yesterday.strftime("%Y-%m-%d")
        yesterday_bets = Bet.objects.filter(participant__race__chart__program__date__lt=yesterday)
        yesterday_venue_codes = []
        venues = []
        for bet in yesterday_bets:
            venue = bet.participant.race.chart.program.venue
            if not venue.code in yesterday_venue_codes:
                venues.append({"code": venue.code, "name": venue.name})
                yesterday_venue_codes.append(venue.code)
        self.context["venues"] = venues
        last_week = today - datetime.timedelta(days=7)
        self.context["last_week"] = last_week.strftime("%Y-%m-%d")

        # self.context["last_month"] = today - datetime.timedelta(days=30)
        # self.context["last_year"] = today - datetime.timedelta(days=365)
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

def delete_exotic_bet(request):
    wager_uuid = request.GET.get('wager_uuid')

    # try:
    #     wager = Quiniela_Wager.objects.get(uuid=wager_uuid)
    # except ObjectDoesNotExist:
    #     try:
    #         wager = Exacta_Wager.objects.get(uuid=wager_uuid)
    #     except ObjectDoesNotExist:
    #         pass
            # try:
            #     wager = Predicted_Trifecta.objects.get(uuid=wager_uuid)
            # except ObjectDoesNotExist:
            #     wager = Sizzle_Superfecta.objects.get(uuid=wager_uuid)
    # wager.delete()


    return JsonResponse({
        "wager_uuid":  wager_uuid})

def make_exotic_bet(request):
    race_uuid = request.GET.get('race_uuid')
    amount = request.GET.get('amount')
    bet_type = request.GET.get('bet_type')

    selected_posts = [char for char in request.GET.get('selected_posts')]
    race = Race.objects.get(uuid=race_uuid)
    # if bet_type == "Q":
    #     new_wager = Quiniela_Wager(
    #         race=race,
    #         amount=amount,
    #         left=race.get_participant(int(selected_posts[0])),
    #         right=race.get_participant(int(selected_posts[1]))
    #     )
    # elif bet_type == "E":
    #     new_wager = Exacta_Wager(
    #         race=race,
    #         amount=amount,
    #         win=race.get_participant(int(selected_posts[0])),
    #         place=race.get_participant(int(selected_posts[1]))
    #     )
    # elif bet_type == "T":
    #     pass
    #     # new_wager = Predicted_Trifecta(
    #     #     race=race,
    #     #     amount=amount,
    #     #     win=race.get_participant(int(selected_posts[0])),
    #     #     place=race.get_participant(int(selected_posts[1])),
    #     #     show=race.get_participant(int(selected_posts[2])),
    #     # )
    # elif bet_type == "TB":
    #     pass
    # elif bet_type == "SB":
    #     pass
    # elif bet_type == "S":
    #     new_wager = Sizzle_Superfecta(
    #         race=race,
    #         amount=amount,
    #         win=race.get_participant(int(selected_posts[0])),
    #         place=race.get_participant(int(selected_posts[1])),
    #         show=race.get_participant(int(selected_posts[2])),
    #         fourth=race.get_participant(int(selected_posts[3])),
    #     )
    # new_wager.set_fields_to_base()
    # new_wager.save()

    # return JsonResponse({
    #     'type': new_wager.get_name(),
    #     'wager_uuid': new_wager.uuid,
    #     'posts': selected_posts,
    #     'amount': amount,
    #     'race_uuid': race_uuid })

def make_bet(request):
    print(request.GET.__dict__)
    participant_id = request.GET.get('participant_id')
    participant = Participant.objects.get(
        uuid=participant_id)
    bet_names = [char for char in request.GET.get('bet_types')]
    amount = request.GET.get('amount')
    bet_update = {'W': 0, 'P': 0, 'S': 0}
    for bet_name in bet_names:
        print(bet_name)
        type = StraightBetType.objects.get(name=bet_name)
        try:
            bet = Straight_Bet.objects.get(
                participant = participant,
                type = type
            )
        except ObjectDoesNotExist:
            new_bet = Straight_Bet(
                participant = participant,
                type = type
            )
            new_bet.set_fields_to_base()
            bet = new_bet
            new_bet.save()
        bet.purchase_amount = float(amount)
        bet.save()
        bet_update[bet_name] = bet.purchase_amount

    print(bet.uuid)

    return JsonResponse({
        'bets': bet_update,
        'participant_id': participant_id })

def clear_bets(request):
    participant_id = request.GET.get('participant_id')
    participant = Participant.objects.get(
        uuid=participant_id)
    for bet in Straight_Bet.objects.filter(
        participant=participant):
        bet.delete()
    return JsonResponse({
        'participant_id': participant_id })


def load_bets(request):
    chart = Chart.objects.get(
        uuid=request.GET.get('chart_id'))
    races = chart.get_predicted_races()
    url = 'bet_table.html'
    return render(request, url, {'races': races})



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

def get_venue_bets(request):
    today = datetime.datetime.now().date()
    date = request.GET.get('date')
    venue_code = request.GET.get('venue_code')
    bets = Bet.objects.filter(
        participant__race__chart__program__date__gte=date,
        participant__final__isnull=False,
        participant__race__chart__program__venue__code=venue_code)
    bets_object = {
        "W": [],
        "P": [],
        "S": []
    }
    for bet in bets:
        type = bet.type.name
        bets_object[type].append(bet.get_return() - bet.amount)

    bet_types = []
    averages = []
    profits = []
    for each in bets_object.keys():
        bet_types.append(each)
        profit = sum(bets_object[each])
        if len(bets_object[each]) > 0:
            average = profit/len(bets_object[each])
        else:
            average = 0
        profits.append(profit)
        averages.append(average)

    #TODO: get graded averages



    return JsonResponse({
        'types': bet_types,
        'profits': profits,
        'averages': averages,
        'raw_win': bets_object["W"]})

def get_bets(request):
    today = datetime.datetime.now().date()
    date = request.GET.get('date')

    bets = Bet.objects.filter(
        participant__race__chart__program__date__gte=date,
        participant__final__isnull=False)
    # bets = Bet.objects.all()
    # if request.GET.get('venue_code'):
    #     venue_code = request.GET.get('venue_code')
    #     bets = bets.filter(
    #         participant__race__chart__program__venue__code=venue_code)
    # venue_bets = {}
    # graded_bets = {}
    # type_bets = {}
    # post_bets = {}
    bets_object = {}
    venues = []
    for bet in bets:
        venue_code = bet.participant.race.chart.program.venue.code
        if not venue_code in venues:
            venues.append(venue_code)
        if not venue_code in bets_object.keys():
            bets_object[venue_code] = []
        bets_object[venue_code].append(bet.get_return() - bet.amount)

    print(bets_object)
    profits = []
    averages = []

    for venue_code in venues:
        print(venue_code)
        venue_bets = bets_object[venue_code]
        venue_profits = sum(venue_bets)
        profits.append(venue_profits)
        averages.append(venue_profits/len(venue_bets))
    print(profits)
    print(averages)
        # venue_code = bet.participant.race.chart.program.venue.code
        # post = bet.participant.post
        # bet_type = bet.type.name
        # grade = bet.participant.race.grade.name
        # bet_ret = bet.get_return()
        # if not venue_code in venue_bets.keys():
        #     venue_bets[venue_code] = []
        # venue_bets[venue_code].append({
        #     "profit": bet_ret - bet.amount,
        #     "grade": grade,
        # })
        # if not bet_type in type_bets.keys():
        #     type_bets[bet_type] = []
        # type_bets[bet_type].append({
        #     "profit": bet_ret - bet.amount,
        #     "grade": grade,
        # })
        # if not grade in graded_bets.keys():
        #     graded_bets[grade] = []
        # graded_bets[grade].append({
        #     "profit": bet_ret - bet.amount,
        #     "type": type,
        # })




    return JsonResponse({
        'venues': venues,
        'profits': profits,
        'averages': averages})


def logout_view(request):
    logout(request)
    response = redirect('/')
    return response
