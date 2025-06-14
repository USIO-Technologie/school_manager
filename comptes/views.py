from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.db.models import Sum
import calendar

from academiques.models import Eleve, Classe, Cours
from finance.models import Paiement
from presence.models import Presence

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


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class DashboardDataView(View):
    def get(self, request, *args, **kwargs):
        filt = {}
        if request.ecole and not request.user.is_superuser:
            filt["ecole"] = request.ecole

        effectif = Eleve.objects.filter(**filt).count()
        n_classes = Classe.objects.filter(**filt).count()
        n_cours = Cours.objects.filter(**filt).count()
        total_encaisse = (
            Paiement.objects.filter(**filt).aggregate(total=Sum("montant"))[
                "total"
            ]
            or 0
        )

        today = timezone.localdate()
        present_count = Presence.objects.filter(
            date=today, present=True, **filt
        ).count()
        taux_presence = (present_count / effectif * 100) if effectif else 0

        labels = []
        values = []
        for i in range(11, -1, -1):
            year = today.year
            month = today.month - i
            while month <= 0:
                month += 12
                year -= 1
            start_month = timezone.datetime(year, month, 1).date()
            last_day = calendar.monthrange(year, month)[1]
            end_month = timezone.datetime(year, month, last_day).date()
            total = (
                Paiement.objects.filter(
                    date_paiement__range=(start_month, end_month), **filt
                ).aggregate(total=Sum("montant"))["total"]
                or 0
            )
            labels.append(f"{month:02d}/{year}")
            values.append(float(total))

        timeline = []
        payments = Paiement.objects.filter(**filt).order_by("-created_at")[:5]
        absents = Presence.objects.filter(present=False, **filt).order_by("-date")[:5]
        new_students = Eleve.objects.filter(**filt).order_by("-created_at")[:5]
        for p in payments:
            timeline.append({"date": p.created_at, "msg": f"{p.eleve} a payé {p.montant}"})
        for pr in absents:
            timeline.append({"date": pr.date, "msg": f"{pr.eleve} absent"})
        for e in new_students:
            timeline.append({"date": e.created_at, "msg": f"Nouvel élève {e}"})
        timeline.sort(key=lambda x: x["date"], reverse=True)
        timeline_msgs = [t["msg"] for t in timeline[:5]]

        data = {
            "effectif": effectif,
            "n_classes": n_classes,
            "n_cours": n_cours,
            "total_encaisse": float(total_encaisse),
            "taux_presence": round(taux_presence, 2),
            "chart": {"labels": labels, "values": values},
            "timeline": timeline_msgs,
        }
        return JsonResponse(data)
