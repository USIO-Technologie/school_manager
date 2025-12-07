"""
Vues web pour l'application app_profile.

Ce module contient les vues Django pour l'interface web
de l'authentification et de la gestion des profils.
"""

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Q, Avg, Max, Min
from django.utils import timezone
from django.urls import reverse_lazy
from datetime import timedelta, date
from decimal import Decimal
import json

from .models import Profile, DocumentVerification, UserSession, LoginHistory, TrustedDevice, UserPreferences, Student, Teacher, Parent
from app_config.models import Country, UserRole, Role, Permission, UserPermission
from app_config.permissions import has_permission, is_admin, PermissionRequiredMixin, get_user_permissions
from django.shortcuts import get_object_or_404

# Imports pour les autres apps
try:
    from app_academic.models import AcademicYear, Class, Subject, Course, Schedule
    ACADEMIC_AVAILABLE = True
except ImportError:
    ACADEMIC_AVAILABLE = False

try:
    from app_grades.models import StudentGrade, Assessment, ReportCard
    from app_grades.services.utils import calculate_student_average, calculate_overall_average
    GRADES_AVAILABLE = True
except ImportError:
    GRADES_AVAILABLE = False

try:
    from app_attendance.models import Attendance, Absence
    from app_attendance.services.utils import calculate_attendance_rate
    ATTENDANCE_AVAILABLE = True
except ImportError:
    ATTENDANCE_AVAILABLE = False
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
import io


# ==================== AUTHENTICATION VIEWS ====================

class LoginView(View):
    """
    Vue pour afficher la page de connexion.
    
    Cette vue gère l'affichage du formulaire de login.
    Si l'utilisateur est déjà authentifié, il est redirigé vers le dashboard.
    """
    
    def get(self, request):
        """
        Affiche la page de connexion.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Rendu du template login.html
        """
        # Si l'utilisateur est déjà authentifié, rediriger vers le dashboard
        if request.user.is_authenticated:
            return redirect('app_profile:dashboard_redirect')
        
        from .forms import LoginForm
        form = LoginForm()
        return render(request, 'app_profile/login.html', {'form': form})
    
    def post(self, request):
        """
        Gère la soumission du formulaire de login.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Redirection ou rendu du template avec erreur
        """
        from .forms import LoginForm
        
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Bienvenue {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'app_profile:dashboard_redirect')
                return redirect(next_url)
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            # Ne pas envoyer de message générique si le formulaire a des erreurs de validation
            # Les erreurs de validation seront affichées directement sur les champs
            # Seulement envoyer un message si c'est vraiment nécessaire
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
            elif form.errors:
                # Si il y a des erreurs de champ, on peut envoyer un message plus spécifique
                # mais généralement les erreurs de validation sont affichées sur les champs
                pass
        
        return render(request, 'app_profile/login.html', {'form': form})


class WebLoginView(View):
    """
    Vue pour gérer le login web via AJAX.
    
    Cette vue authentifie l'utilisateur en session Django après
    avoir reçu les credentials via AJAX.
    """
    
    def post(self, request):
        """
        Authentifie l'utilisateur et crée une session Django.
        
        Args:
            request: Objet Request avec username et password dans le body JSON
        
        Returns:
            JsonResponse: Réponse JSON avec le statut de l'authentification
        """
        try:
            # Parser le body JSON
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '')
            remember_me = data.get('remember_me', False)
            
            # Valider les données
            if not username or not password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le nom d\'utilisateur et le mot de passe sont requis'
                }, status=400)
            
            # Authentifier l'utilisateur
            user = authenticate(request, username=username, password=password)
            
            if user is None:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Nom d\'utilisateur ou mot de passe incorrect'
                }, status=401)
            
            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Votre compte est désactivé. Veuillez contacter le support.'
                }, status=403)
            
            # Créer la session Django
            auth_login(request, user)
            
            # Gérer "Se souvenir de moi" - définir la durée de la session
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semaines
            else:
                request.session.set_expiry(0)  # Session expire à la fermeture du navigateur
            
            # Récupérer les informations du profil
            is_verified = False
            completion_rate = 0
            full_name = user.get_full_name() or user.username
            
            try:
                if hasattr(user, 'profile'):
                    is_verified = user.profile.is_verified
                    completion_rate = user.profile.completion_rate
                    if user.profile.full_name:
                        full_name = user.profile.full_name
                    elif user.profile.name and user.profile.firstname:
                        full_name = f"{user.profile.firstname} {user.profile.name}"
            except Exception:
                pass
            
            # Retourner la réponse de succès
            return JsonResponse({
                'status': 'success',
                'message': 'Connexion réussie',
                'username': user.username,
                'full_name': full_name,
                'is_verified': is_verified,
                'completion_rate': completion_rate
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Données JSON invalides'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Une erreur est survenue: {str(e)}'
            }, status=500)


class LogoutView(View):
    """
    Vue pour déconnecter l'utilisateur (web).
    
    Cette vue gère la déconnexion de l'utilisateur en supprimant
    la session Django et en redirigeant vers la page de login.
    """
    
    def post(self, request):
        """
        Déconnecte l'utilisateur et redirige vers la page de login.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Redirection vers la page de login
        """
        auth_logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
        return redirect('app_profile:login')
    
    def get(self, request):
        """
        Déconnecte l'utilisateur via GET (pour les liens simples).
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Redirection vers la page de login
        """
        auth_logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
        return redirect('app_profile:login')


# ==================== DASHBOARD VIEWS ====================

class StandardDashboardView(View):
    """
    Vue pour afficher un dashboard adaptatif selon les rôles et permissions.
    
    Ce dashboard affiche des informations différentes selon les rôles
    et permissions de l'utilisateur.
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche le dashboard avec des informations adaptées aux rôles et permissions.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Rendu du template dashboard.html
        """
        user = request.user
        context = {
            'user': user,
        }
        
        # Récupérer l'année scolaire courante
        current_year = None
        if ACADEMIC_AVAILABLE:
            try:
                current_year = AcademicYear.objects.filter(is_current=True, is_active=True).first()
            except Exception:
                pass
        
        # Récupérer le profil si disponible
        try:
            if hasattr(user, 'profile'):
                profile = user.profile
                context['profile'] = profile
                
                # Récupérer les rôles de l'utilisateur
                user_roles = UserRole.objects.filter(
                    profile=profile,
                    is_active=True,
                    role__is_active=True
                ).select_related('role').order_by('role__name')
                
                context['user_roles'] = user_roles
                context['roles_list'] = [ur.role.name for ur in user_roles]
                
                # Récupérer les permissions de l'utilisateur
                all_permissions = get_user_permissions(profile)
                context['user_permissions'] = all_permissions
                context['permissions_list'] = [p.codename for p in all_permissions]
                
                # Vérifier les permissions spécifiques
                context['can_view_profile'] = has_permission(profile, 'view_profile', 'app_profile')
                context['can_edit_profile'] = has_permission(profile, 'edit_profile', 'app_profile')
                context['can_verify_profile'] = has_permission(profile, 'verify_profile', 'app_profile')
                context['can_view_all_users'] = has_permission(profile, 'view_all_profiles', 'app_profile')
                context['can_manage_verifications'] = has_permission(profile, 'manage_verifications', 'app_profile')
                context['can_assign_permissions'] = has_permission(profile, 'assign_role_permissions', 'app_config')
                context['is_admin'] = is_admin(profile)
                
                # Statistiques selon les permissions
                stats = {}
                dashboard_data = {}
                
                # ========== DASHBOARD ÉTUDIANT ==========
                if hasattr(profile, 'student'):
                    student = profile.student
                    stats['is_student'] = True
                    stats['student_number'] = student.student_number
                    
                    if GRADES_AVAILABLE and current_year:
                        # Notes récentes (dernières 5)
                        recent_grades = StudentGrade.objects.filter(
                            student=student,
                            is_active=True,
                            assessment__academic_year=current_year
                        ).select_related('assessment', 'assessment__subject').order_by('-assessment__date')[:5]
                        dashboard_data['recent_grades'] = recent_grades
                        
                        # Moyenne générale
                        overall_avg = calculate_overall_average(student.id, current_year.id) if current_year else None
                        dashboard_data['overall_average'] = float(overall_avg) if overall_avg else None
                        
                        # Moyennes par matière
                        subject_averages = []
                        if ACADEMIC_AVAILABLE:
                            subjects = Subject.objects.filter(is_active=True)
                            for subject in subjects:
                                avg = calculate_student_average(student.id, subject.id, current_year.id) if current_year else None
                                if avg is not None:
                                    subject_averages.append({
                                        'subject': subject,
                                        'average': float(avg)
                                    })
                        dashboard_data['subject_averages'] = subject_averages
                        
                        # Prochains examens (7 prochains jours)
                        today = timezone.now().date()
                        next_week = today + timedelta(days=7)
                        upcoming_assessments = Assessment.objects.filter(
                            class_section=student.class_section,
                            academic_year=current_year,
                            date__gte=today,
                            date__lte=next_week,
                            is_active=True
                        ).select_related('subject', 'category').order_by('date')[:10]
                        dashboard_data['upcoming_assessments'] = upcoming_assessments
                        
                        # Données pour graphique d'évolution des notes
                        chart_data = []
                        if ACADEMIC_AVAILABLE:
                            for subject in subjects[:5]:  # Top 5 matières
                                grades = StudentGrade.objects.filter(
                                    student=student,
                                    assessment__subject=subject,
                                    assessment__academic_year=current_year,
                                    is_active=True,
                                    is_absent=False,
                                    score__isnull=False
                                ).select_related('assessment').order_by('assessment__date')
                                
                                subject_grades = [float(g.score) for g in grades]
                                if subject_grades:
                                    chart_data.append({
                                        'subject': subject.name,
                                        'grades': subject_grades
                                    })
                        dashboard_data['grades_chart_data'] = chart_data
                    
                    if ATTENDANCE_AVAILABLE:
                        # Taux de présence (mois en cours)
                        today = timezone.now().date()
                        month_start = date(today.year, today.month, 1)
                        attendance_rate = calculate_attendance_rate(student.id, month_start, today)
                        dashboard_data['attendance_rate'] = float(attendance_rate) if attendance_rate else None
                        
                        # Absences non justifiées
                        unexcused_absences = Absence.objects.filter(
                            student=student,
                            is_justified=False,
                            is_active=True
                        ).count()
                        dashboard_data['unexcused_absences'] = unexcused_absences
                        
                        # Présence mensuelle pour graphique
                        monthly_data = []
                        for i in range(6):  # 6 derniers mois
                            month_date = today - timedelta(days=30*i)
                            month_start = date(month_date.year, month_date.month, 1)
                            if month_start.month == 12:
                                month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
                            else:
                                month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)
                            
                            rate = calculate_attendance_rate(student.id, month_start, month_end)
                            monthly_data.append({
                                'month': month_start.strftime('%b %Y'),
                                'rate': float(rate) if rate else 0
                            })
                        monthly_data.reverse()
                        dashboard_data['monthly_attendance'] = monthly_data
                    
                    if ACADEMIC_AVAILABLE:
                        # Emploi du temps du jour
                        today_weekday = today.weekday()  # 0 = Monday, 6 = Sunday
                        today_schedule = Schedule.objects.filter(
                            class_section=student.class_section,
                            day_of_week=today_weekday,
                            is_active=True
                        ).select_related('subject', 'teacher').order_by('start_time')
                        dashboard_data['today_schedule'] = today_schedule
                
                # ========== DASHBOARD ENSEIGNANT ==========
                elif hasattr(profile, 'teacher'):
                    teacher = profile.teacher
                    stats['is_teacher'] = True
                    stats['teacher_number'] = teacher.teacher_number
                    
                    if ACADEMIC_AVAILABLE:
                        # Classes enseignées
                        classes_taught = teacher.classes.filter(is_active=True).select_related('grade', 'academic_year')
                        dashboard_data['classes_taught'] = classes_taught
                        
                        # Matières enseignées
                        subjects_taught = teacher.subjects.filter(is_active=True)
                        dashboard_data['subjects_taught'] = subjects_taught
                        
                        # Prochains cours (aujourd'hui)
                        today_weekday = timezone.now().date().weekday()
                        today_courses = Schedule.objects.filter(
                            teacher=teacher,
                            day_of_week=today_weekday,
                            is_active=True
                        ).select_related('class_section', 'subject').order_by('start_time')
                        dashboard_data['today_courses'] = today_courses
                    
                    if GRADES_AVAILABLE and current_year:
                        # Évaluations à corriger (non notées)
                        assessments_to_grade = Assessment.objects.filter(
                            teacher=teacher,
                            academic_year=current_year,
                            is_active=True
                        ).exclude(
                            id__in=StudentGrade.objects.filter(
                                is_active=True,
                                score__isnull=False
                            ).values_list('assessment_id', flat=True)
                        ).select_related('subject', 'class_section').order_by('date')[:10]
                        dashboard_data['assessments_to_grade'] = assessments_to_grade
                        
                        # Statistiques des notes par classe
                        class_stats = []
                        if ACADEMIC_AVAILABLE:
                            for class_obj in classes_taught:
                                grades = StudentGrade.objects.filter(
                                    student__class_section=class_obj,
                                    assessment__academic_year=current_year,
                                    is_active=True,
                                    is_absent=False,
                                    score__isnull=False
                                )
                                
                                if grades.exists():
                                    avg = grades.aggregate(Avg('score'))['score__avg']
                                    class_stats.append({
                                        'class': {
                                            'id': class_obj.id,
                                            'name': class_obj.name,
                                            'code': class_obj.code
                                        },
                                        'average': float(avg) if avg else None,
                                        'total_students': Student.objects.filter(class_section=class_obj, is_active=True).count(),
                                        'graded_count': grades.values('student').distinct().count()
                                    })
                        dashboard_data['class_stats'] = class_stats
                    
                    if ATTENDANCE_AVAILABLE:
                        # Absences récentes des élèves
                        recent_absences = Absence.objects.filter(
                            student__class_section__in=classes_taught if ACADEMIC_AVAILABLE else [],
                            is_active=True
                        ).select_related('student', 'student__profile').order_by('-start_date')[:10]
                        dashboard_data['recent_absences'] = recent_absences
                
                # ========== DASHBOARD PARENT ==========
                elif hasattr(profile, 'parent'):
                    parent = profile.parent
                    stats['is_parent'] = True
                    stats['parent_number'] = parent.parent_number
                    
                    # Enfants
                    children = parent.children.filter(is_active=True).select_related('profile')
                    dashboard_data['children'] = children
                    
                    if GRADES_AVAILABLE and current_year:
                        # Notes récentes de tous les enfants
                        recent_grades = StudentGrade.objects.filter(
                            student__in=children,
                            is_active=True,
                            assessment__academic_year=current_year
                        ).select_related('student', 'student__profile', 'assessment', 'assessment__subject').order_by('-assessment__date')[:10]
                        dashboard_data['children_recent_grades'] = recent_grades
                    
                    if ATTENDANCE_AVAILABLE:
                        # Absences récentes
                        recent_absences = Absence.objects.filter(
                            student__in=children,
                            is_active=True
                        ).select_related('student', 'student__profile').order_by('-start_date')[:10]
                        dashboard_data['children_recent_absences'] = recent_absences
                        
                        # Taux de présence par enfant
                        children_attendance = []
                        today = timezone.now().date()
                        month_start = date(today.year, today.month, 1)
                        for child in children:
                            rate = calculate_attendance_rate(child.id, month_start, today)
                            unexcused = Absence.objects.filter(
                                student=child,
                                is_justified=False,
                                is_active=True
                            ).count()
                            children_attendance.append({
                                'child': {
                                    'id': child.id,
                                    'profile': {
                                        'full_name': child.profile.full_name,
                                        'user': {
                                            'username': child.profile.user.username
                                        }
                                    }
                                },
                                'attendance_rate': float(rate) if rate else None,
                                'unexcused_absences': unexcused
                            })
                        dashboard_data['children_attendance'] = children_attendance
                    
                    if GRADES_AVAILABLE and current_year:
                        # Prochains examens des enfants
                        today = timezone.now().date()
                        next_week = today + timedelta(days=7)
                        upcoming_assessments = Assessment.objects.filter(
                            class_section__student__in=children,
                            academic_year=current_year,
                            date__gte=today,
                            date__lte=next_week,
                            is_active=True
                        ).select_related('subject', 'class_section').order_by('date')[:10]
                        dashboard_data['children_upcoming_assessments'] = upcoming_assessments
                
                # ========== DASHBOARD ADMIN ==========
                if context['is_admin']:
                    # Statistiques globales
                    stats['total_users'] = Profile.objects.filter(is_active=True).count()
                    stats['total_students'] = Student.objects.filter(is_active=True).count()
                    stats['total_teachers'] = Teacher.objects.filter(is_active=True).count()
                    stats['total_parents'] = Parent.objects.filter(is_active=True).count()
                    
                    if ACADEMIC_AVAILABLE:
                        stats['total_classes'] = Class.objects.filter(is_active=True).count()
                        stats['total_subjects'] = Subject.objects.filter(is_active=True).count()
                    
                    stats['pending_verifications'] = DocumentVerification.objects.filter(status='pending').count()
                    stats['total_verifications'] = DocumentVerification.objects.count()
                    
                    # Activités récentes (dernières créations)
                    recent_profiles = Profile.objects.filter(is_active=True).order_by('-created_at')[:5]
                    dashboard_data['recent_profiles'] = recent_profiles
                    
                    # Graphiques de tendances
                    if GRADES_AVAILABLE and current_year:
                        # Répartition des notes
                        grade_distribution = StudentGrade.objects.filter(
                            assessment__academic_year=current_year,
                            is_active=True,
                            is_absent=False,
                            score__isnull=False
                        ).aggregate(
                            excellent=Count('id', filter=Q(score__gte=16)),
                            good=Count('id', filter=Q(score__gte=14, score__lt=16)),
                            average=Count('id', filter=Q(score__gte=10, score__lt=14)),
                            poor=Count('id', filter=Q(score__lt=10))
                        )
                        dashboard_data['grade_distribution'] = grade_distribution
                
                context['stats'] = stats
                context['dashboard_data'] = dashboard_data
                context['current_year'] = current_year
                context['today'] = timezone.now().date()
                
        except Profile.DoesNotExist:
            pass
        
        return render(request, 'app_profile/dashboard.html', context)


class DashboardRedirectView(View):
    """
    Vue pour rediriger vers le dashboard approprié.
    
    Cette vue redirige l'utilisateur vers son dashboard
    en fonction de son type de profil et de ses rôles.
    Si l'utilisateur n'a pas de rôles, affiche un dashboard standard.
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Redirige vers le dashboard approprié.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Redirection vers le dashboard ou rendu du dashboard standard
        """
        user = request.user
        
        # Vérifier si l'utilisateur a un profil
        if not hasattr(user, 'profile'):
            # Pas de profil, afficher le dashboard standard
            return redirect('app_profile:standard_dashboard')
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            # Profil n'existe pas, afficher le dashboard standard
            return redirect('app_profile:standard_dashboard')
        
        # Vérifier si l'utilisateur a des rôles actifs
        has_roles = UserRole.objects.filter(
            profile=profile,
            is_active=True,
            role__is_active=True
        ).exists()
        
        if not has_roles:
            # Pas de rôles, afficher le dashboard standard
            return redirect('app_profile:standard_dashboard')
        
        # L'utilisateur a des rôles, vérifier s'il a la permission de voir le profil
        if has_permission(profile, 'view_profile', 'app_profile'):
            return redirect('app_profile:profile_view')
        else:
            # Pas de permission pour voir le profil, afficher le dashboard standard
            return redirect('app_profile:standard_dashboard')


# ==================== PROFILE VIEWS ====================

class ProfileView(PermissionRequiredMixin, View):
    """
    Vue pour afficher et gérer le profil utilisateur.
    
    Cette vue affiche le profil avec toutes les statistiques.
    
    Requiert la permission: view_profile
    """
    
    required_permission = 'view_profile'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche la page de profil avec statistiques.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Rendu du template profile.html
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé. Veuillez contacter le support.')
            return redirect('app_profile:login')
        
        # Récupérer les pays pour le formulaire
        countries = Country.objects.filter(is_active=True).order_by('name')
        
        # Calculer les statistiques
        stats = self._calculate_statistics(profile)
        
        context = {
            'profile': profile,
            'countries': countries,
            'stats': stats,
        }
        
        return render(request, 'app_profile/profile.html', context)
    
    def _calculate_statistics(self, profile):
        """
        Calcule les statistiques du profil.
        
        Args:
            profile: Instance du modèle Profile
        
        Returns:
            dict: Dictionnaire contenant toutes les statistiques
        """
        stats = {
            'completion_rate': profile.completion_rate,
            'is_verified': profile.is_verified,
        }
        
        # Statistiques selon le rôle
        if hasattr(profile, 'student'):
            stats['is_student'] = True
            stats['student_number'] = profile.student.student_number
        elif hasattr(profile, 'teacher'):
            stats['is_teacher'] = True
            stats['teacher_number'] = profile.teacher.teacher_number
        elif hasattr(profile, 'parent'):
            stats['is_parent'] = True
            stats['parent_number'] = profile.parent.parent_number
        
        return stats


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(PermissionRequiredMixin, View):
    """
    Vue pour afficher et mettre à jour le profil utilisateur.
    
    Cette vue affiche un formulaire d'édition du profil et traite
    les soumissions pour mettre à jour les informations.
    
    Requiert la permission: edit_profile
    """
    
    required_permission = 'edit_profile'
    required_resource = 'app_profile'
    
    def get(self, request):
        """
        Affiche le formulaire d'édition du profil.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Rendu du template profile_edit.html
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé. Veuillez contacter le support.')
            return redirect('app_profile:profile_view')
        
        # Récupérer les pays pour le formulaire
        countries = Country.objects.filter(is_active=True).order_by('name')
        from .forms import ProfileForm
        form = ProfileForm(instance=profile)
        
        context = {
            'profile': profile,
            'countries': countries,
            'form': form,
        }
        
        return render(request, 'app_profile/profile_edit.html', context)
    
    def post(self, request):
        """
        Met à jour le profil de l'utilisateur.
        
        Args:
            request: Objet Request Django avec les données du formulaire
        
        Returns:
            HttpResponse: Redirection vers la page de profil ou d'édition
        """
        try:
            user = request.user
            
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                messages.error(request, 'Profil non trouvé. Veuillez contacter le support.')
                return redirect('app_profile:profile_view')
            
            from .forms import ProfileForm
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil mis à jour avec succès!')
                return redirect('app_profile:profile_view')
            else:
                # Afficher les erreurs de validation
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
                
                countries = Country.objects.filter(is_active=True).order_by('name')
                return render(request, 'app_profile/profile_edit.html', {
                    'profile': profile,
                    'countries': countries,
                    'form': form,
                })
            
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating profile: {str(e)}\n{traceback.format_exc()}")
            
            messages.error(request, f'Une erreur inattendue s\'est produite: {str(e)}')
            return redirect('app_profile:profile_update')


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    """
    Vue pour changer le mot de passe de l'utilisateur.
    
    Cette vue affiche un formulaire de changement de mot de passe
    et traite les soumissions pour mettre à jour le mot de passe.
    """
    
    def get(self, request):
        """
        Affiche le formulaire de changement de mot de passe.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Rendu du template change_password.html
        """
        from .forms import ChangePasswordForm
        form = ChangePasswordForm(user=request.user)
        return render(request, 'app_profile/change_password.html', {'form': form})
    
    def post(self, request):
        """
        Change le mot de passe de l'utilisateur.
        
        Args:
            request: Objet Request Django avec les données du formulaire
        
        Returns:
            HttpResponse: Redirection vers la page de profil ou de changement de mot de passe
        """
        try:
            user = request.user
            from .forms import ChangePasswordForm
            
            form = ChangePasswordForm(user, request.POST)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Le mot de passe a été changé avec succès.')
                return redirect('app_profile:profile_view')
            else:
                # Afficher les erreurs de validation
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
                
                return render(request, 'app_profile/change_password.html', {'form': form})
            
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error changing password: {str(e)}\n{traceback.format_exc()}")
            
            messages.error(request, f'Une erreur inattendue s\'est produite: {str(e)}')
            return redirect('app_profile:change_password')


@method_decorator(login_required, name='dispatch')
class ProfileVerificationView(PermissionRequiredMixin, View):
    """
    Vue pour consulter les documents de vérification KYC (lecture seule).
    
    Requiert la permission: verify_profile
    """
    
    required_permission = 'verify_profile'
    required_resource = 'app_profile'
    
    def get(self, request):
        """
        Affiche l'historique des documents de vérification.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Rendu du template profile_verification.html
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé. Veuillez contacter le support.')
            return redirect('app_profile:profile_view')
        
        # Récupérer les documents de vérification existants
        documents = DocumentVerification.objects.filter(profile=profile).order_by('-created_at')
        
        context = {
            'profile': profile,
            'documents': documents,
        }
        
        return render(request, 'app_profile/profile_verification.html', context)


@method_decorator(login_required, name='dispatch')
class VerificationManagementView(PermissionRequiredMixin, View):
    """
    Vue pour gérer les vérifications de profils (admin).
    
    Cette vue permet aux administrateurs de voir et gérer
    toutes les demandes de vérification.
    
    Requiert la permission: manage_verifications
    """
    
    required_permission = 'manage_verifications'
    required_resource = 'app_profile'
    
    def get(self, request):
        """
        Affiche la liste des vérifications en attente.
        
        Args:
            request: Objet Request Django
        
        Returns:
            HttpResponse: Rendu du template verification_management.html
        """
        # Filtrer par statut si fourni
        status_filter = request.GET.get('status', 'pending')
        
        # Récupérer les vérifications
        verifications = DocumentVerification.objects.select_related('profile', 'verified_by').all()
        
        if status_filter and status_filter != 'all':
            verifications = verifications.filter(status=status_filter)
        
        verifications = verifications.order_by('-created_at')
        
        # Statistiques
        stats = {
            'pending': DocumentVerification.objects.filter(status='pending').count(),
            'under_review': DocumentVerification.objects.filter(status='under_review').count(),
            'approved': DocumentVerification.objects.filter(status='approved').count(),
            'rejected': DocumentVerification.objects.filter(status='rejected').count(),
            'total': DocumentVerification.objects.count(),
        }
        
        context = {
            'verifications': verifications,
            'stats': stats,
            'current_status': status_filter,
        }
        
        return render(request, 'app_profile/verification_management.html', context)


@method_decorator(login_required, name='dispatch')
class VerificationDetailView(PermissionRequiredMixin, View):
    """
    Vue pour voir les détails d'une vérification et l'approuver/rejeter.
    
    Requiert la permission: manage_verifications
    """
    
    required_permission = 'manage_verifications'
    required_resource = 'app_profile'
    
    def get(self, request, verification_id):
        """
        Affiche les détails d'une vérification.
        
        Args:
            request: Objet Request Django
            verification_id: ID de la vérification
        
        Returns:
            HttpResponse: Rendu du template verification_detail.html
        """
        try:
            verification = DocumentVerification.objects.select_related(
                'profile', 'profile__user', 'verified_by'
            ).get(id=verification_id)
        except DocumentVerification.DoesNotExist:
            messages.error(request, 'Vérification non trouvée.')
            return redirect('app_profile:verification_management')
        
        context = {
            'verification': verification,
        }
        
        return render(request, 'app_profile/verification_detail.html', context)
    
    def post(self, request, verification_id):
        """
        Approuve ou rejette une vérification.
        
        Args:
            request: Django Request object
            verification_id: Verification ID
        
        Returns:
            HttpResponse: Redirect to verification management
        """
        try:
            verification = DocumentVerification.objects.get(id=verification_id)
        except DocumentVerification.DoesNotExist:
            messages.error(request, 'Vérification non trouvée.')
            return redirect('app_profile:verification_management')
        
        action = request.POST.get('action')
        
        if action == 'approve':
            notes = request.POST.get('admin_notes', '').strip()
            verification.approve(verified_by=request.user, notes=notes)
            messages.success(request, f'Le profil de {verification.profile.full_name} a été vérifié avec succès.')
        
        elif action == 'reject':
            reason = request.POST.get('rejection_reason', '').strip()
            if not reason:
                messages.error(request, 'La raison du rejet est requise.')
                return redirect('app_profile:verification_detail', verification_id=verification_id)
            
            verification.reject(verified_by=request.user, reason=reason)
            messages.success(request, f'La vérification de {verification.profile.full_name} a été rejetée.')
        
        elif action == 'review':
            verification.set_under_review()
            messages.info(request, 'La vérification a été marquée comme en cours de vérification.')
        
        else:
            messages.error(request, 'Action invalide.')
        
        return redirect('app_profile:verification_management')


@method_decorator(login_required, name='dispatch')
class ProfileRolesManagementView(View):
    """
    Vue pour gérer les rôles et permissions d'un profil depuis la page de profil.
    
    Cette vue permet aux administrateurs ou utilisateurs avec les permissions
    appropriées de gérer les rôles et permissions d'un profil spécifique.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Vérifie que l'utilisateur a la permission d'accéder à cette page.
        """
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Vous n\'avez pas la permission d\'accéder à cette page.')
            return redirect('app_profile:dashboard_redirect')
        
        # Vérifier si l'utilisateur est admin ou a la permission assign_role_permissions ou manage_permissions
        user_profile = request.user.profile
        has_assign = has_permission(user_profile, 'assign_role_permissions', 'app_config')
        has_manage = has_permission(user_profile, 'manage_permissions', 'app_config')
        is_user_admin = is_admin(user_profile)
        
        if not (has_assign or has_manage or is_user_admin):
            messages.error(request, 'Vous n\'avez pas la permission d\'accéder à cette page.')
            return redirect('app_profile:dashboard_redirect')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, profile_id):
        """
        Affiche la page de gestion des rôles et permissions d'un profil.
        
        Args:
            request: Objet Request Django
            profile_id: ID du profil à gérer
        
        Returns:
            HttpResponse: Page de gestion des rôles et permissions
        """
        # Récupérer le profil à gérer
        profile = get_object_or_404(Profile, id=profile_id, is_active=True)
        
        # Récupérer les rôles de l'utilisateur
        user_roles = UserRole.objects.filter(
            profile=profile,
            is_active=True
        ).select_related('role', 'assigned_by')
        
        # Récupérer les permissions directes (actives uniquement)
        user_permissions = UserPermission.objects.filter(
            profile=profile,
            is_active=True
        ).prefetch_related('permissions', 'granted_by')
        
        # Récupérer toutes les permissions (via rôles et directes)
        all_permissions = get_user_permissions(profile)
        
        # Récupérer tous les rôles et permissions disponibles
        all_roles = Role.objects.filter(is_active=True).order_by('name')
        all_permissions_list = Permission.objects.filter(is_active=True).order_by('resource', 'action', 'name')
        
        # Grouper les permissions par ressource
        permissions_by_resource = {}
        for perm in all_permissions_list:
            if perm.resource not in permissions_by_resource:
                permissions_by_resource[perm.resource] = []
            permissions_by_resource[perm.resource].append(perm)
        
        context = {
            'profile': profile,
            'user_roles': user_roles,
            'user_permissions': user_permissions,
            'all_permissions': all_permissions,
            'all_roles': all_roles,
            'permissions_by_resource': permissions_by_resource,
        }
        
        return render(request, 'app_profile/profile_roles_management.html', context)


@method_decorator(login_required, name='dispatch')
class SecurityView(PermissionRequiredMixin, View):
    """
    Vue pour la gestion de la sécurité du compte.
    
    Affiche :
    - Sessions actives
    - Historique des connexions
    - Appareils de confiance
    
    Requiert la permission: view_profile
    """
    
    required_permission = 'view_profile'
    required_resource = 'app_profile'
    
    def get(self, request):
        """
        Affiche la page de sécurité.
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé.')
            return redirect('app_profile:profile_view')
        
        # Récupérer les sessions actives
        active_sessions = UserSession.objects.filter(
            user=user,
            is_active=True
        ).order_by('-last_activity')
        
        # Récupérer l'historique des connexions (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        login_history = LoginHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:50]  # Limiter à 50 entrées
        
        # Récupérer les appareils de confiance
        trusted_devices = TrustedDevice.objects.filter(
            user=user,
            is_active=True
        ).order_by('-last_used')
        
        # Identifier la session actuelle
        current_session_key = request.session.session_key
        current_session = None
        if current_session_key:
            try:
                current_session = UserSession.objects.get(
                    user=user,
                    session_key=current_session_key,
                    is_active=True
                )
            except UserSession.DoesNotExist:
                pass
        
        context = {
            'profile': profile,
            'active_sessions': active_sessions,
            'login_history': login_history,
            'trusted_devices': trusted_devices,
            'current_session': current_session,
        }
        
        return render(request, 'app_profile/security.html', context)


@method_decorator(login_required, name='dispatch')
class SettingsView(PermissionRequiredMixin, View):
    """
    Vue pour la gestion des paramètres utilisateur.
    
    Permet de gérer :
    - Préférences de langue
    - Préférences de timezone
    - Paramètres de notification
    - Préférences d'affichage
    - Paramètres de confidentialité
    
    Requiert la permission: edit_profile
    """
    
    required_permission = 'edit_profile'
    required_resource = 'app_profile'
    
    def get(self, request):
        """
        Affiche la page des paramètres.
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé.')
            return redirect('app_profile:profile_view')
        
        # Récupérer ou créer les préférences
        preferences, created = UserPreferences.objects.get_or_create(
            profile=profile,
            defaults={
                'language': 'fr',
                'timezone': 'UTC',
            }
        )
        
        # Liste des timezones courantes
        common_timezones = [
            ('UTC', 'UTC'),
            ('Africa/Kinshasa', 'Kinshasa (GMT+1)'),
            ('Africa/Lagos', 'Lagos (GMT+1)'),
            ('Africa/Johannesburg', 'Johannesburg (GMT+2)'),
            ('Europe/Paris', 'Paris (GMT+1/+2)'),
            ('America/New_York', 'New York (GMT-5/-4)'),
            ('America/Los_Angeles', 'Los Angeles (GMT-8/-7)'),
            ('Asia/Tokyo', 'Tokyo (GMT+9)'),
            ('Asia/Shanghai', 'Shanghai (GMT+8)'),
        ]
        
        context = {
            'profile': profile,
            'preferences': preferences,
            'common_timezones': common_timezones,
        }
        
        return render(request, 'app_profile/settings.html', context)
    
    def post(self, request):
        """
        Met à jour les préférences utilisateur.
        """
        try:
            user = request.user
            
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                messages.error(request, 'Profil non trouvé.')
                return redirect('app_profile:profile_view')
            
            # Récupérer ou créer les préférences
            preferences, created = UserPreferences.objects.get_or_create(
                profile=profile
            )
            
            # Mettre à jour les champs
            # Langue
            if 'language' in request.POST:
                preferences.language = request.POST['language']
            
            # Timezone
            if 'timezone' in request.POST:
                preferences.timezone = request.POST['timezone']
            
            # Notifications
            preferences.email_notifications = 'email_notifications' in request.POST
            preferences.sms_notifications = 'sms_notifications' in request.POST
            preferences.push_notifications = 'push_notifications' in request.POST
            preferences.transaction_notifications = 'transaction_notifications' in request.POST
            preferences.security_notifications = 'security_notifications' in request.POST
            
            # Affichage
            if 'theme' in request.POST:
                preferences.theme = request.POST['theme']
            
            if 'items_per_page' in request.POST:
                try:
                    items_per_page = int(request.POST['items_per_page'])
                    if 10 <= items_per_page <= 100:
                        preferences.items_per_page = items_per_page
                except ValueError:
                    pass
            
            # Confidentialité
            if 'profile_visibility' in request.POST:
                preferences.profile_visibility = request.POST['profile_visibility']
            
            preferences.show_email = 'show_email' in request.POST
            preferences.show_phone = 'show_phone' in request.POST
            preferences.allow_search = 'allow_search' in request.POST
            
            preferences.save()
            
            messages.success(request, 'Paramètres mis à jour avec succès!')
            return redirect('app_profile:settings')
            
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating settings: {str(e)}\n{traceback.format_exc()}")
            
            messages.error(request, f'Une erreur s\'est produite: {str(e)}')
            return redirect('app_profile:settings')


# ==================== PASSWORD RESET VIEWS ====================

class PasswordResetRequestView(View):
    """
    Vue pour demander la réinitialisation du mot de passe.
    """
    
    def get(self, request):
        """
        Affiche le formulaire de demande de réinitialisation.
        """
        from .forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()
        return render(request, 'app_profile/password_reset_request.html', {'form': form})
    
    def post(self, request):
        """
        Traite la demande de réinitialisation.
        """
        from .forms import PasswordResetRequestForm
        from django.contrib.auth.views import PasswordResetView
        
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            # Utiliser la vue Django standard pour l'envoi d'email
            return PasswordResetView.as_view(
                template_name='app_profile/password_reset_request.html',
                email_template_name='app_profile/password_reset_email.html',
                subject_template_name='app_profile/password_reset_subject.txt',
                success_url=reverse_lazy('app_profile:password_reset_done')
            )(request)
        
        return render(request, 'app_profile/password_reset_request.html', {'form': form})


class PasswordResetDoneView(View):
    """
    Vue affichée après l'envoi de l'email de réinitialisation.
    """
    
    def get(self, request):
        """
        Affiche le message de confirmation.
        """
        return render(request, 'app_profile/password_reset_done.html')


class PasswordResetConfirmView(View):
    """
    Vue pour confirmer la réinitialisation du mot de passe (avec token).
    """
    
    def get(self, request, uidb64, token):
        """
        Affiche le formulaire de confirmation.
        """
        from .forms import PasswordResetConfirmForm
        from django.contrib.auth.views import PasswordResetConfirmView as DjangoPasswordResetConfirmView
        
        # Utiliser la vue Django standard
        return DjangoPasswordResetConfirmView.as_view(
            template_name='app_profile/password_reset_confirm.html',
            form_class=PasswordResetConfirmForm,
            success_url=reverse_lazy('app_profile:password_reset_complete')
        )(request, uidb64=uidb64, token=token)
    
    def post(self, request, uidb64, token):
        """
        Traite la confirmation de réinitialisation.
        """
        from .forms import PasswordResetConfirmForm
        from django.contrib.auth.views import PasswordResetConfirmView as DjangoPasswordResetConfirmView
        
        # Utiliser la vue Django standard
        return DjangoPasswordResetConfirmView.as_view(
            template_name='app_profile/password_reset_confirm.html',
            form_class=PasswordResetConfirmForm,
            success_url=reverse_lazy('app_profile:password_reset_complete')
        )(request, uidb64=uidb64, token=token)


class PasswordResetCompleteView(View):
    """
    Vue affichée après la réinitialisation réussie du mot de passe.
    """
    
    def get(self, request):
        """
        Affiche le message de succès.
        """
        return render(request, 'app_profile/password_reset_complete.html')
