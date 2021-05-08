from django.views.generic import View
from django.shortcuts import render

class Welcome(View):

    template_name = "welcome.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

class FrontPage(OTPRequiredMixin, View):

    template_name = 'frontpage.html'
    context = {}

    def get(self, request, *args, **kwargs):
        myDate = datetime.now()
        active_venues = Venue.objects.filter(is_active=True)
        self.context["venues"] = active_venues        
