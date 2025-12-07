"""
Utilitaires pour l'application app_attendance.

Ce module contient les fonctions utilitaires pour les calculs de présences.
"""

from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from ..models import Attendance, Absence, AttendanceRule


def calculate_attendance_rate(student_id, start_date, end_date):
    """
    Calcule le taux de présence d'un élève sur une période.
    
    Args:
        student_id: ID de l'élève
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        Decimal: Taux de présence (0-100) ou None
    """
    attendances = Attendance.objects.filter(
        student_id=student_id,
        date__gte=start_date,
        date__lte=end_date,
        is_active=True
    )
    
    if not attendances.exists():
        return None
    
    total = attendances.count()
    present = attendances.filter(status='present').count()
    
    if total == 0:
        return None
    
    rate = (Decimal(present) / Decimal(total)) * Decimal('100')
    return rate


def check_absence_threshold(student_id, rule_id):
    """
    Vérifie si un élève a dépassé le seuil d'absences.
    
    Args:
        student_id: ID de l'élève
        rule_id: ID de la règle
        
    Returns:
        bool: True si le seuil est dépassé
    """
    rule = AttendanceRule.get_rule(rule_id)
    if not rule:
        return False
    
    # Compter les absences non justifiées sur les 30 derniers jours
    start_date = timezone.now().date() - timedelta(days=30)
    absences = Absence.objects.filter(
        student_id=student_id,
        start_date__gte=start_date,
        is_justified=False,
        is_active=True
    )
    
    total_days = 0
    for absence in absences:
        if absence.end_date:
            days = (absence.end_date - absence.start_date).days + 1
        else:
            days = 1
        total_days += days
    
    return total_days >= rule.max_absences


def send_absence_alert(student_id):
    """
    Envoie une alerte pour les absences répétées.
    
    Args:
        student_id: ID de l'élève
        
    Returns:
        bool: True si l'alerte a été envoyée
    """
    # TODO: Implémenter l'envoi d'alerte via Celery
    # Utiliser app_profile.tasks pour envoyer un email/SMS
    return True

