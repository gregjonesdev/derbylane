from datetime import datetime

from django.views.generic import View
from django.shortcuts import render

from two_factor.views.mixins import OTPRequiredMixin

from rawdat.models import (
    Venue,
)


class Welcome(OTPRequiredMixin, View):

    template_name = "welcome.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

class FrontPage(View):

    template_name = 'frontpage.html'
    context = {}

    def get(self, request, *args, **kwargs):
        active_venues = Venue.objects.filter(is_active=True)
        myDate = datetime.now()
        self.context["venues"] = active_venues
        self.context["today"] = myDate.strftime("%A, %B %-d")

        return render(request, self.template_name, self.context)
