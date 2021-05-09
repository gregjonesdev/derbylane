from django.views.generic import View
from django.shortcuts import render

from two_factor.views.mixins import OTPRequiredMixin


class Welcome(OTPRequiredMixin, View):

    template_name = "welcome.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)
