from decimal import Decimal
import uuid
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
import datetime as dt
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from comptes.models import EmailOTP, Profil
from comptes.tests import User
from comptes.utils import as_datetime, send_otp_to_email
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

    def post(self, request, *args, **kwargs):
        email = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            profil = user.profil
            # Redirection selon le nombre d'écoles
            if profil.ecoles.count() == 1:
                request.session["ecole_id"] = profil.ecoles.first().id
                return JsonResponse({"success": True, "redirect_url": str(reverse_lazy("dashboard"))})
            return JsonResponse({"success": True, "redirect_url": str(reverse_lazy("comptes:choisir_ecole"))})
        else:
            return JsonResponse({"success": False, "error": "Identifiants invalides."})

    def get_success_url(self):
        profil = self.request.user.profil # type: ignore
        if profil.ecoles.count() == 1:
            self.request.session["ecole_id"] = profil.ecoles.first().id
            return reverse_lazy("dashboard")
        return reverse_lazy("comptes:choisir_ecole")

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(TemplateView):
    template_name = "comptes/register.html"

    def post(self, request):
        step = request.POST.get("step")
        email = request.POST.get("username")
        name = request.POST.get("name")
        password = request.POST.get("password")

        print(f"*********************Register step: {step}, email: {email}, name: {name}, password: {password}")
        
        if step == "register":
            otp_entry, created = EmailOTP.objects.get_or_create(email=email)
            print(f"*********************Register otp_entry: {otp_entry}, created: {created}")
            otp_entry.generer_otp()
            return JsonResponse({"status": "otp_sent"})

        elif step == "verify":
            code = request.POST.get("otp")
            print(f"*********************Register verify code: {code}")
            try:
                otp_entry = EmailOTP.objects.get(email=email)
                result = otp_entry.verifier_otp(code)

                if result == "ok":
                    if not User.objects.filter(username=email).exists():
                        user = User.objects.create_user(username=email, email=email, password=password)
                        Profil.objects.create(user=user, nom=name, matricule=str(uuid.uuid4()))
                    return JsonResponse({"status": "verified"})
                elif result == "expired":
                    return JsonResponse({"status": "expired"})
                elif result == "blocked":
                    return JsonResponse({"status": "blocked"})
                else:
                    return JsonResponse({"status": "invalid"})

            except EmailOTP.DoesNotExist:
                return JsonResponse({"status": "invalid"})

        elif step == "resend":
            try:
                otp_entry, _ = EmailOTP.objects.get_or_create(email=email)
                otp_entry.generer_otp()
                return JsonResponse({"status": "otp_resent"})
            except Exception:
                return JsonResponse({"status": "error"})

        return JsonResponse({"status": "error"})

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
    template_name = "comptes/dashboard.html"


class DashboardDataView(View):
    """API JSON consommée par dashboard.js"""
    # ------------------------------------------------------------------
    # GET /dashboard/data/
    # ------------------------------------------------------------------
    def get(self, request, *args, **kwargs):
        # --------- 1) Filtre École ------------------------------------
        filt = {}
        if request.ecole and not request.user.is_superuser:
            filt["ecole"] = request.ecole

        # --------- 2) KPI principaux ---------------------------------
        effectif      = Eleve .objects.filter(**filt).count()
        n_classes     = Classe.objects.filter(**filt).count()
        n_cours       = Cours .objects.filter(**filt).count()
        total_encaisse = (
            Paiement.objects.filter(**filt)
            .aggregate(total=Sum("montant"))["total"] or Decimal("0")
        )

        # taux de présence du jour ------------------------------------
        today          = timezone.localdate()
        present_count  = Presence.objects.filter(date=today, present=True, **filt).count()
        taux_presence  = round((present_count / effectif * 100), 2) if effectif else 0

        # --------- 3) Graphique CA (12 derniers mois) ----------------
        labels, values = [], []
        for i in range(11, -1, -1):                               # 11→0 (mois -11 à courant)
            year  = today.year
            month = today.month - i
            while month <= 0:                                     # rebascule sur année précédente
                month += 12
                year  -= 1
            start_month = dt.date(year, month, 1)
            last_day    = calendar.monthrange(year, month)[1]
            end_month   = dt.date(year, month, last_day)

            total = (
                Paiement.objects.filter(
                    date_paiement__range=(start_month, end_month), **filt
                )
                .aggregate(total=Sum("montant"))["total"] or Decimal("0")
            )
            labels.append(f"{month:02d}/{year}")
            values.append(float(total))

        # --------- 4) Timeline (5 derniers évènements) ---------------
        timeline = []

        # Paiements récents
        for p in Paiement.objects.filter(**filt).order_by("-created_at")[:5]:
            timeline.append({
                "date": as_datetime(p.created_at),
                "msg" : f"{p.eleve} a payé {p.montant} $",
            })

        # Absences récentes
        for pr in Presence.objects.filter(present=False, **filt).order_by("-date")[:5]:
            timeline.append({
                "date": as_datetime(pr.date),
                "msg" : f"{pr.eleve} absent",
            })

        # Nouveaux élèves
        for e in Eleve.objects.filter(**filt).order_by("-created_at")[:5]:
            timeline.append({
                "date": as_datetime(e.created_at),
                "msg" : f"Nouvel élève {e}",
            })

        # Tri décroissant puis découpe aux 5 plus récents
        timeline.sort(key=lambda x: x["date"], reverse=True)
        timeline_msgs = [ev["msg"] for ev in timeline[:5]]

        # --------- 5) Payload JSON -----------------------------------
        data = {
            "effectif"       : effectif,
            "n_classes"      : n_classes,
            "n_cours"        : n_cours,
            "total_encaisse" : float(total_encaisse),
            "taux_presence"  : taux_presence,
            "chart"          : {"labels": labels, "values": values},
            "timeline"       : timeline_msgs,
        }
        return JsonResponse(data)