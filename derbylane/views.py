from datetime import datetime

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
        self.context["today"] = today.strftime("%A, %B %-d")

        return render(request, self.template_name, self.context)
