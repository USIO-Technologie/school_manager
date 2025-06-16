import datetime as dt
from django.utils import timezone
from django.core.mail import send_mail
import random
from comptes.models import EmailOTP

def as_datetime(value: dt.date | dt.datetime) -> dt.datetime:
    """
    Retourne un datetime *aware* (fuseau local) quelle que soit l'entrée.
    - Si value est datetime → converti au fuseau courant (localtime).
    - Si value est date     → combiné à 00:00 puis rendu aware.
    """
    # 1) convertir en datetime naïf si besoin
    if isinstance(value, dt.datetime):
        dt_val = value
    else:  # simple date
        dt_val = dt.datetime.combine(value, dt.time.min)

    # 2) le rendre aware dans le TZ courant
    if timezone.is_naive(dt_val):
        dt_val = timezone.make_aware(dt_val, timezone.get_current_timezone())
    else:
        dt_val = timezone.localtime(dt_val, timezone.get_current_timezone())

    return dt_val

def send_otp_to_email(email):
    otp = str(random.randint(100000, 999999))
    EmailOTP.objects.update_or_create(email=email, defaults={"otp": otp})
    send_mail(
        subject="Votre code de vérification",
        message=f"Votre code est : {otp}",
        from_email="nsoleoslo15@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )