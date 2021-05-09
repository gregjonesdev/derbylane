from django.views.generic import View
from django.shortcuts import render

class Welcome(View):

    template_name = "welcome.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)
