from django.contrib.auth import logout
from datetime import datetime
from django.shortcuts import redirect

from django.views.generic import View
from django.shortcuts import render

from two_factor.views.mixins import OTPRequiredMixin

from rawdat.models import (
    Venue, Chart
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
        today = datetime.now()
        venues = []
        for chart in Chart.objects.filter(program__date = today):
            venue = chart.program.venue
            if not venue in venues:
                venues.append(venue)
        self.context["venues"] = venues
        self.context["today"] = today.strftime("%A, %B %-d")

        return render(request, self.template_name, self.context)

def load_charts(request):
    venue = Venue.objects.get(
        code=request.GET.get('venue_code'))
    charts = Chart.objects.filter(
        program__venue=venue,
        program__date=datetime.now()
    )
    return render(
        request,
        'load_charts.html', {'charts': charts, })


def logout_view(request):
    logout(request)
    response = redirect('/')
    return response
