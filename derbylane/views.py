import os, fnmatch
import py7zr
from django.utils.timezone import localdate
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
import datetime
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from django.views.generic import View
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse, Http404
from two_factor.views.mixins import OTPRequiredMixin

from rawdat.models import (
    Venue,
    Chart,
    CronJob,
    Program,
    Participant,
    Bet,
    StraightBetType
)

class Welcome(OTPRequiredMixin, View):

    template_name = "welcome.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

class FrontPage(OTPRequiredMixin, View):

    template_name = 'frontpage.html'
    context = {}

    def get(self, request, *args, **kwargs):
        datestring = request.GET.get("date")
        if datestring:
            date_obj = datetime.datetime.strptime(datestring, "%Y-%m-%d").date()
        else:
            date_obj = localdate()
        self.context["previous"] = (date_obj - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        next_day = date_obj + datetime.timedelta(days=1)
        self.context["next"] = next_day.strftime("%Y-%m-%d")
        self.context["next_day_scheduled"] = Program.objects.filter(date=next_day).exists()
        self.context["date_header"] = date_obj.strftime("%A, %B %-d")
        self.context["is_past"] = localdate() > date_obj
        self.context["datestring"] = datestring
        self.context["charts"] = Chart.objects.filter(program__date=date_obj)
        return render(request, self.template_name, self.context)



class ProfileView(OTPRequiredMixin, View):

    template_name = 'profile.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)


class VenueView(OTPRequiredMixin, View):

    template_name = 'venues.html'
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["venues"] = Venue.objects.filter(is_active=True)
        return render(request, self.template_name, self.context)

class ScanView(OTPRequiredMixin, View):

    template_name = 'scans.html'
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["scans"] = CronJob.objects.all()[:10]
        return render(request, self.template_name, self.context)

class DownloadsView(OTPRequiredMixin, View):

    template_name = 'downloads.html'
    context = {}

    def get(self, request, *args, **kwargs):
        filenames = fnmatch.filter(os.listdir('arff'), '*_model.arff')
        self.context["filenames"] = filenames
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        print("post")
        files = request.POST.getlist('files')
        # print(os.listdir("arff"))
        # self.context["filenames"] = os.listdir("arff")
        file_path = 'downloads.7z'
        if len(files) > 0:
            with py7zr.SevenZipFile(
                file_path,
                'w',
                # password=config('FILE_PASSWORD')) as archive:
                password='') as archive:
                for filename in files:
                    archive.write("arff/{}".format(filename))
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/*")
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    return response
            raise Http404
        else:
            response = redirect('frontpage')
            return response


class ResultsView(OTPRequiredMixin, View):

    template_name = 'results.html'
    context = {}

    def get(self, request, *args, **kwargs):
        print("Results view")
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


class AnalysisView(OTPRequiredMixin, View):

    template_name = 'analysis.html'
    context = {}

    def get(self, request, *args, **kwargs):
        # try:
        #     target_date = datetime.datetime.fromisoformat(
        #         request.GET.get("date"))
        # except:
        #     target_date = localdate()
        # bets = Bet.objects.filter(
        #     participant__race__chart__program__date=target_date).order_by(
        #         'participant__race__chart', 'participant__race')
        # self.context["bets"] = bets
        # self.context["day"] = target_date.strftime("%A")
        # self.context["date"] = target_date.strftime("%Y-%m-%d")
        return render(request, self.template_name, self.context)


class UploadsView(OTPRequiredMixin, View):

    template_name = 'uploads.html'
    context = {}

    def get(self, request, *args, **kwargs):
        print("get uplaodz")

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        print("post uplaodz")
        print(request.FILES)


class PasswordReset(OTPRequiredMixin, auth_views.PasswordResetView):

    context = {}
    def get(self, request, *args, **kwargs):
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
    participant = Participant.objects.get(
        uuid=request.GET.get('participant_id'))
    for bet_name in [char for char in request.GET.get('bet_types')]:
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
            bet.amount = amount
            bet.save()

    return JsonResponse({
        'bets': participant.get_purchased_wagers(),
        'none': participant.prediction.get_bets(),
        'enabled': request.user.is_staff})


def load_bets(request):
    print("load bets")
    print(datetime.datetime.now())
    chart = Chart.objects.get(
        uuid=request.GET.get('chart_id'))

    current_date = datetime.datetime.now().date()

    if chart.is_complete() or current_date > chart.program.date:
        url = "results.html"
    else:
        url = "load_bets.html"

    print("render url: {}".format(url))
    races = chart.race_set.filter(
        grade__value__gt=0)
    # races = chart.race_set.all()
    print(request.user)
    return render(
        request,
        url, {
            'races': races,
            'user': request.user })


def logout_view(request):
    logout(request)
    response = redirect('/')
    return response
