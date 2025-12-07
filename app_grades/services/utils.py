"""
Utilitaires pour l'application app_grades.

Ce module contient les fonctions utilitaires pour les calculs de notes et moyennes.
"""

from decimal import Decimal
from django.db.models import Avg, Sum, Count, Q
from ..models import StudentGrade, Assessment, ReportCard


def calculate_student_average(student_id, subject_id, year_id=None):
    """
    Calcule la moyenne d'un élève pour une matière.
    
    Args:
        student_id: ID de l'élève
        subject_id: ID de la matière
        year_id: ID de l'année scolaire (optionnel)
        
    Returns:
        Decimal: Moyenne calculée ou None
    """
    return StudentGrade.calculate_average(student_id, subject_id, year_id)


def calculate_class_average(class_id, assessment_id):
    """
    Calcule la moyenne de classe pour une évaluation.
    
    Args:
        class_id: ID de la classe
        assessment_id: ID de l'évaluation
        
    Returns:
        Decimal: Moyenne de classe ou None
    """
    grades = StudentGrade.objects.filter(
        assessment_id=assessment_id,
        student__class_section_id=class_id,
        is_active=True,
        is_absent=False,
        score__isnull=False
    )
    
    if not grades.exists():
        return None
    
    # Calculer la moyenne pondérée
    total_score = Decimal('0')
    total_coefficient = Decimal('0')
    
    for grade in grades:
        coefficient = grade.assessment.coefficient
        total_score += grade.score * coefficient
        total_coefficient += coefficient
    
    if total_coefficient == 0:
        return None
    
    return total_score / total_coefficient


def calculate_overall_average(student_id, year_id):
    """
    Calcule la moyenne générale d'un élève pour une année scolaire.
    
    Args:
        student_id: ID de l'élève
        year_id: ID de l'année scolaire
        
    Returns:
        Decimal: Moyenne générale ou None
    """
    from app_academic.models import Subject
    
    subjects = Subject.objects.filter(is_active=True)
    averages = []
    total_coefficient = Decimal('0')
    
    for subject in subjects:
        avg = calculate_student_average(student_id, subject.id, year_id)
        if avg is not None:
            coefficient = subject.coefficient
            averages.append(avg * coefficient)
            total_coefficient += coefficient
    
    if not averages or total_coefficient == 0:
        return None
    
    total_score = sum(averages)
    return total_score / total_coefficient


def generate_report_card_pdf(report_card_id):
    """
    Génère un PDF pour un bulletin de notes.
    
    Args:
        report_card_id: ID du bulletin
        
    Returns:
        bytes: Contenu du PDF ou None
    """
    # TODO: Implémenter la génération de PDF
    # Utiliser reportlab ou weasyprint
    return None

