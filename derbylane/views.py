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
from django.http import JsonResponse, HttpResponse, Http404
from two_factor.views.mixins import OTPRequiredMixin

from rawdat.models import (
    Venue,
    Chart,
    CronJob,
    Program,
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
        today = localdate()
        charts = []
        for chart in Chart.objects.filter(program__date=today):
            if chart.has_predictions():
                charts.append(chart)
        self.context["charts"] = charts

        self.context["today"] = today.strftime("%A, %B %-d")

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
        today = localdate()
        yesterday = today - datetime.timedelta(days=1)
        programs = Program.objects.filter(date=yesterday)
        self.context["yesterday"] = yesterday
        self.context["programs"] = programs
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
    print("make bets")
    # print(request)
    # return render(
    #     request,
    #     'make_bet.html',
    #     {
    #         'test': 'hi'
    #     })

def load_bets(request):
    chart = Chart.objects.get(
        uuid=request.GET.get('chart_id'))
    races = chart.race_set.filter(
        grade__value__gt=0)
    # races = chart.race_set.all()
    print(request.user.email)
    return render(
        request,
        'load_bets.html', {
            'races': races,
            'user': request.user,
            'program': chart.program,
            'venue': chart.program.venue })


def logout_view(request):
    logout(request)
    response = redirect('/')
    return response
