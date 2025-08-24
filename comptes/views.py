import calendar
import datetime as dt
import uuid
from decimal import Decimal

from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from academiques.models import Eleve, Classe, Cours
from comptes.models import EmailOTP, Profil, PasswordResetToken
from comptes.tests import User
from comptes.utils import as_datetime
from finance.models import Paiement
from presence.models import Presence
from school_manager import settings

User = get_user_model()
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
                return JsonResponse({"success": True, "redirect_url": str(reverse_lazy("comptes:dashboard"))})
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
            from_email = settings.EMAIL_HOST_USER
            send_mail(
                subject="Email OTP",
                message=f"votre code otp  : {otp_entry.otp}",
                from_email=from_email,
                recipient_list=[email],
                fail_silently=False
            )
            return JsonResponse({"status": "otp_sent"})

        elif step == "verify":
            code = request.POST.get("otp")
            print(f"*********************Register verify code: {code}")
            try:
                otp_entry = EmailOTP.objects.get(email=email)
                result = otp_entry.verifier_otp(code)

                if result == "ok":
                    if not User.objects.filter(email=email).exists():
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


class ResetPasswordRequestView(View):
    def get(self, request):
        return render(request, 'comptes/password_reset.html')

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            from_email = settings.EMAIL_HOST_USER
            token_obj = PasswordResetToken.objects.create(user=user)
            reset_link = request.build_absolute_uri(f"/reset-password-confirm/{token_obj.token}/")
            send_mail(
                subject="Réinitialisez votre mot de passe",
                message=f"Cliquez ici pour réinitialiser votre mot de passe : {reset_link}",
                from_email=from_email,
                recipient_list=[email],
                fail_silently=False
            )
            return JsonResponse({"message": "Lien envoyé ! Vérifiez votre email."})
        except User.DoesNotExist:
            return JsonResponse({"message": "Email introuvable."})

# views.py (suite)

class ResetPasswordConfirmView(View):
    def get(self, request, token):
        try:
            # Conversion explicite en UUID
            token = uuid.UUID(str(token))
            token_obj = PasswordResetToken.objects.get(token=token)
            if not token_obj.is_valid():
                return JsonResponse({'message': 'Lien expiré'}, status=400)
            return render(request, 'comptes/password_reset_confirm.html', {'token': token})
        except (PasswordResetToken.DoesNotExist, ValueError):
            return JsonResponse({'message': 'Lien invalide'}, status=400)

    @method_decorator(csrf_exempt)  # Pour éviter les problèmes de CSRF si AJAX
    def post(self, request, token):
        try:
            token = uuid.UUID(str(token))
            token_obj = PasswordResetToken.objects.get(token=token)
            if not token_obj.is_valid():
                return JsonResponse({'message': 'Lien expiré'}, status=400)

            password = request.POST.get('password')
            if not password:
                return JsonResponse({'message': 'Mot de passe manquant'}, status=400)

            user = token_obj.user
            user.password = make_password(password)
            user.save()
            token_obj.delete()

            return JsonResponse({'message': 'Mot de passe réinitialisé avec succès'})
        except (PasswordResetToken.DoesNotExist, ValueError):
            return JsonResponse({'message': 'Lien invalide'}, status=400)


class ChoisirEcoleView(LoginRequiredMixin, TemplateView):
    template_name = "comptes/choisir_ecole.html"
    login_url = "comptes:login"  # adapte selon ton nom d'URL

    def get_context_data(self, **kwargs):
        print("-----------------get_context_data Choisir Ecole -------------")
        ctx = super().get_context_data(**kwargs)
        profil = getattr(self.request.user, "profil", None)
        ctx["ecoles"] = profil.ecoles.all() if profil else []
        return ctx

    def post(self, request, *args, **kwargs):
        print("-----------------POST Choisir Ecole -------------")
        profil = getattr(request.user, "profil", None)
        print(f"-------------profil : {profil}")
        if not profil:
            # user connecté mais sans profil utilisable
            return HttpResponseForbidden("Profil utilisateur manquant.")

        ecole_id = request.POST.get("ecole_id")
        try:
            ecole_id = int(ecole_id)  # sécurise le type
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Identifiant d'école invalide.")

        # Vérifie l’appartenance de l’école au profil
        try:
            ecole = profil.ecoles.get(pk=ecole_id)
        except profil.ecoles.model.DoesNotExist:
            return HttpResponseForbidden("École non autorisée.")

        request.session["ecole_id"] = ecole.pk
        # Optionnel: invalider des caches liés à l’ancienne école ici
        return redirect("/dashboard")  # adapte si besoin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "comptes/dashboard.html"
    login_url = "comptes:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.session.get("ecole_id"):
            return redirect("comptes:choisir_ecole")

        # Récupération des informations de l'école
        profil = self.request.user.profil
        ecole = profil.ecoles.get(id=self.request.session["ecole_id"])

        context.update({
            "ecole": ecole,
            "nom_ecole": ecole.nom,
            "ville_ecole": ecole.ville,
            "pays_ecole": ecole.pays,
        })

        return context


class DashboardDataView(LoginRequiredMixin, View):
    """API JSON pour les données du tableau de bord"""

    def get(self, request, *args, **kwargs):
        if not request.session.get("ecole_id"):
            return JsonResponse({"error": "No school selected"}, status=403)

        ecole_id = request.session["ecole_id"]

        try:
            ecole = request.user.profil.ecoles.get(id=ecole_id)
        except:
            return JsonResponse({"error": "School not found"}, status=404)

        # --------- 2) KPI principaux ---------------------------------
        effectif = (
            Eleve.objects
            .filter(ecole=ecole, is_active=True)
            .count()
        )

        n_classes = (
            Classe.objects
            .filter(eleve__ecole=ecole)
            .distinct()
            .count()
        )

        n_cours = (
            Cours.objects
            .filter(classe__eleve__ecole=ecole)
            .distinct()
            .count()
        )

        total_encaisse = (
            Paiement.objects
            .filter(ecole=ecole)
            .aggregate(total=Sum("montant"))["total"] or Decimal("0")
        )

        # --------- 3) Taux de présence du jour ------------------------------------
        today = timezone.localtime().date()  # Utilisation de localtime().date() pour avoir la date locale
        present_count = (
            Presence.objects
            .filter(
                eleve__ecole=ecole,
                date=today,
                present=True
            )
            .count()
        )
        taux_presence = round((present_count / effectif * 100), 1) if effectif else 0

        # --------- 4) Graphique CA (12 derniers mois) ----------------
        labels, values = [], []
        current_date = timezone.localtime()

        for i in range(11, -1, -1):
            # Calcul de la date de début et fin du mois
            date = current_date - dt.timedelta(days=current_date.day - 1) - dt.timedelta(days=30 * i)
            start_month = date.replace(day=1)
            if date.month == 12:
                end_month = date.replace(year=date.year + 1, month=1, day=1) - dt.timedelta(days=1)
            else:
                end_month = date.replace(month=date.month + 1, day=1) - dt.timedelta(days=1)

            total = (
                Paiement.objects
                .filter(
                    ecole=ecole,
                    date_paiement__range=(start_month.date(), end_month.date())
                )
                .aggregate(total=Sum("montant"))["total"] or Decimal("0")
            )

            labels.append(f"{start_month.strftime('%m/%Y')}")
            values.append(float(total))

        # --------- 5) Timeline (5 derniers évènements) ---------------
        timeline = []

        # Paiements récents avec leurs relations
        paiements = (
            Paiement.objects
            .filter(ecole=ecole)
            .select_related('eleve')
            .order_by("-created_at")[:5]
        )
        for p in paiements:
            timeline.append({
                "date": as_datetime(p.created_at),
                "msg": f"{p.eleve.prenom} {p.eleve.nom} a payé {p.montant} $",
                "type": "paiement"
            })

        # Absences récentes
        absences = (
            Presence.objects
            .filter(eleve__ecole=ecole, present=False)
            .select_related('eleve')
            .order_by("-date")[:5]
        )
        for a in absences:
            timeline.append({
                "date": as_datetime(a.date),
                "msg": f"{a.eleve.prenom} {a.eleve.nom} absent",
                "type": "absence"
            })

        # Nouveaux élèves
        nouveaux_eleves = (
            Eleve.objects
            .filter(ecole=ecole)
            .order_by("-created_at")[:5]
        )
        for e in nouveaux_eleves:
            timeline.append({
                "date": as_datetime(e.created_at),
                "msg": f"Nouvel élève {e.prenom} {e.nom}",
                "type": "nouveau"
            })

        # Tri par date et limitation
        timeline.sort(key=lambda x: x["date"], reverse=True)
        timeline_msgs = [ev["msg"] for ev in timeline[:5]]

        # --------- 6) Réponse JSON -----------------------------------
        data = {
            "effectif": effectif,
            "n_classes": n_classes,
            "n_cours": n_cours,
            "total_encaisse": float(total_encaisse),
            "taux_presence": taux_presence,
            "chart": {
                "labels": labels,
                "values": values
            },
            "timeline": timeline_msgs,
        }

        return JsonResponse(data)