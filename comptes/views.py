from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden

# Create your views here.
class HomeView(View):
    template_name = 'comptes/home.html'
    def get(self, request):
       return render (request, self.template_name)

class CustomLoginView(LoginView):
    template_name = "comptes/login.html"

    def get_success_url(self):
        profil = self.request.user.profil # type: ignore
        if profil.ecoles.count() == 1:
            self.request.session["ecole_id"] = profil.ecoles.first().id
            return reverse_lazy("dashboard")         # adapte si besoin
        return reverse_lazy("comptes:choisir_ecole")


class ChoisirEcoleView(TemplateView):
    template_name = "comptes/choisir_ecole.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ecoles"] = self.request.user.profil.ecoles.all() # type: ignore
        return ctx

    def post(self, request, *args, **kwargs):
        ecole_id = request.POST.get("ecole_id")
        profil   = request.user.profil

        try:
            ecole = profil.ecoles.get(pk=ecole_id)
        except profil.ecoles.model.DoesNotExist:
            return HttpResponseForbidden("École non autorisée.")

        request.session["ecole_id"] = ecole.id
        return redirect("dashboard")                  # vue d'accueil
