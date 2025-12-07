"""
Vues CRUD pour l'application app_profile.

Ce module contient les vues Django pour les opérations CRUD
sur les profils, élèves, enseignants et parents.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy

from .models import Profile, Student, Teacher, Parent, LoginHistory
from .forms import ProfileForm, StudentForm, TeacherForm, ParentForm, PhotoUploadForm
from app_config.models import Country, UserRole, Role, Permission, UserPermission
from app_config.permissions import has_permission, is_admin, PermissionRequiredMixin, get_user_permissions


# ==================== PROFILE CRUD ====================

class ProfileListView(PermissionRequiredMixin, ListView):
    """
    Vue pour lister tous les profils.
    
    Requiert la permission: view_profile (admin)
    """
    model = Profile
    template_name = 'app_profile/profile_list.html'
    context_object_name = 'profiles'
    paginate_by = 20
    required_permission = 'view_all_profiles'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        """
        Récupère la liste des profils avec filtres.
        """
        queryset = Profile.objects.filter(is_active=True).select_related('user', 'country')
        
        # Filtre par recherche
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Filtre par rôle
        role = self.request.GET.get('role', '')
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['role_choices'] = Profile.ROLE_CHOICES
        return context


class ProfileDetailView(PermissionRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un profil.
    
    Requiert la permission: view_profile
    """
    model = Profile
    template_name = 'app_profile/profile_detail.html'
    context_object_name = 'profile'
    required_permission = 'view_profile'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Profile.objects.filter(is_active=True).select_related('user', 'country')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        
        # Vérifier si le profil a des relations Student, Teacher, Parent
        context['is_student'] = hasattr(profile, 'student')
        context['is_teacher'] = hasattr(profile, 'teacher')
        context['is_parent'] = hasattr(profile, 'parent')
        
        if context['is_student']:
            context['student'] = profile.student
        if context['is_teacher']:
            context['teacher'] = profile.teacher
        if context['is_parent']:
            context['parent'] = profile.parent
        
        # Récupérer les rôles
        context['user_roles'] = UserRole.objects.filter(
            profile=profile,
            is_active=True
        ).select_related('role')
        
        return context


class ProfileCreateView(PermissionRequiredMixin, CreateView):
    """
    Vue pour créer un nouveau profil.
    
    Requiert la permission: create_profile (admin)
    """
    model = Profile
    form_class = ProfileForm
    template_name = 'app_profile/profile_create.html'
    required_permission = 'create_profile'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        """
        Sauvegarde le profil et affiche un message de succès.
        """
        messages.success(self.request, 'Profil créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_profile:profile_detail', kwargs={'pk': self.object.pk})


class ProfileAdminUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Vue pour modifier un profil existant (admin).
    
    Requiert la permission: edit_profile
    """
    model = Profile
    form_class = ProfileForm
    template_name = 'app_profile/profile_admin_update.html'
    required_permission = 'edit_profile'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Profile.objects.filter(is_active=True)
    
    def form_valid(self, form):
        """
        Sauvegarde le profil et affiche un message de succès.
        """
        messages.success(self.request, 'Profil modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_profile:profile_detail', kwargs={'pk': self.object.pk})


# ==================== STUDENT CRUD ====================

class StudentListView(PermissionRequiredMixin, ListView):
    """
    Vue pour lister tous les élèves.
    
    Requiert la permission: view_student
    """
    model = Student
    template_name = 'app_profile/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    required_permission = 'view_student'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        """
        Récupère la liste des élèves avec filtres.
        """
        queryset = Student.get_active_students()
        
        # Filtre par recherche
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(profile__full_name__icontains=search) |
                Q(student_number__icontains=search) |
                Q(class_level__icontains=search)
            )
        
        # Filtre par niveau de classe
        class_level = self.request.GET.get('class_level', '')
        if class_level:
            queryset = queryset.filter(class_level=class_level)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['class_level_filter'] = self.request.GET.get('class_level', '')
        return context


class StudentDetailView(PermissionRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un élève (fiche élève).
    
    Requiert la permission: view_student
    """
    model = Student
    template_name = 'app_profile/student_detail.html'
    context_object_name = 'student'
    required_permission = 'view_student'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Student.get_active_students()


class StudentCreateView(PermissionRequiredMixin, CreateView):
    """
    Vue pour créer un nouvel élève.
    
    Requiert la permission: create_student
    """
    model = Student
    form_class = StudentForm
    template_name = 'app_profile/student_create.html'
    required_permission = 'create_student'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les profils disponibles sans élève
        profiles_without_student = Profile.objects.filter(
            is_active=True
        ).exclude(
            student__isnull=False
        ).select_related('user')
        context['available_profiles'] = profiles_without_student
        return context
    
    def form_valid(self, form):
        """
        Sauvegarde l'élève et définit created_by.
        """
        form.instance.created_by = self.request.user
        # Récupérer le profil sélectionné
        profile_id = self.request.POST.get('profile_id')
        if profile_id:
            profile = get_object_or_404(Profile, id=profile_id, is_active=True)
            form.instance.profile = profile
            # Mettre à jour le rôle du profil
            profile.role = 'student'
            profile.save()
            # Générer le numéro d'élève si vide
            if not form.instance.student_number:
                from .services.utils import generate_student_number
                form.instance.student_number = generate_student_number()
        else:
            messages.error(self.request, 'Veuillez sélectionner un profil.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Élève créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_profile:student_detail', kwargs={'pk': self.object.pk})


class StudentUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Vue pour modifier un élève existant.
    
    Requiert la permission: edit_student
    """
    model = Student
    form_class = StudentForm
    template_name = 'app_profile/student_update.html'
    required_permission = 'edit_student'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Student.get_active_students()
    
    def form_valid(self, form):
        """
        Sauvegarde l'élève et définit updated_by.
        """
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Élève modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_profile:student_detail', kwargs={'pk': self.object.pk})


class MyStudentProfileView(View):
    """
    Vue pour afficher "Mon profil élève".
    
    Affiche le profil de l'élève connecté.
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche le profil élève de l'utilisateur connecté.
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé.')
            return redirect('app_profile:login')
        
        # Vérifier si l'utilisateur est un élève
        if not hasattr(profile, 'student'):
            messages.error(request, 'Vous n\'êtes pas un élève.')
            return redirect('app_profile:profile_view')
        
        student = profile.student
        
        context = {
            'profile': profile,
            'student': student,
        }
        
        return render(request, 'app_profile/my_student_profile.html', context)


# ==================== TEACHER CRUD ====================

class TeacherListView(PermissionRequiredMixin, ListView):
    """
    Vue pour lister tous les enseignants.
    
    Requiert la permission: view_teacher
    """
    model = Teacher
    template_name = 'app_profile/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 20
    required_permission = 'view_teacher'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        """
        Récupère la liste des enseignants avec filtres.
        """
        queryset = Teacher.get_active_teachers()
        
        # Filtre par recherche
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(profile__full_name__icontains=search) |
                Q(teacher_number__icontains=search) |
                Q(specialization__icontains=search) |
                Q(department__icontains=search)
            )
        
        # Filtre par département
        department = self.request.GET.get('department', '')
        if department:
            queryset = queryset.filter(department=department)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['department_filter'] = self.request.GET.get('department', '')
        return context


class TeacherDetailView(PermissionRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un enseignant (fiche enseignant).
    
    Requiert la permission: view_teacher
    """
    model = Teacher
    template_name = 'app_profile/teacher_detail.html'
    context_object_name = 'teacher'
    required_permission = 'view_teacher'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Teacher.get_active_teachers()


class TeacherCreateView(PermissionRequiredMixin, CreateView):
    """
    Vue pour créer un nouvel enseignant.
    
    Requiert la permission: create_teacher
    """
    model = Teacher
    form_class = TeacherForm
    template_name = 'app_profile/teacher_create.html'
    required_permission = 'create_teacher'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les profils disponibles sans enseignant
        profiles_without_teacher = Profile.objects.filter(
            is_active=True
        ).exclude(
            teacher__isnull=False
        ).select_related('user')
        context['available_profiles'] = profiles_without_teacher
        return context
    
    def form_valid(self, form):
        """
        Sauvegarde l'enseignant et définit created_by.
        """
        form.instance.created_by = self.request.user
        # Récupérer le profil sélectionné
        profile_id = self.request.POST.get('profile_id')
        if profile_id:
            profile = get_object_or_404(Profile, id=profile_id, is_active=True)
            form.instance.profile = profile
            # Mettre à jour le rôle du profil
            profile.role = 'teacher'
            profile.save()
            # Générer le numéro d'enseignant si vide
            if not form.instance.teacher_number:
                from .services.utils import generate_teacher_number
                form.instance.teacher_number = generate_teacher_number()
        else:
            messages.error(self.request, 'Veuillez sélectionner un profil.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Enseignant créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_profile:teacher_detail', kwargs={'pk': self.object.pk})


class TeacherUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Vue pour modifier un enseignant existant.
    
    Requiert la permission: edit_teacher
    """
    model = Teacher
    form_class = TeacherForm
    template_name = 'app_profile/teacher_update.html'
    required_permission = 'edit_teacher'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Teacher.get_active_teachers()
    
    def form_valid(self, form):
        """
        Sauvegarde l'enseignant et définit updated_by.
        """
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Enseignant modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_profile:teacher_detail', kwargs={'pk': self.object.pk})


class MyTeacherProfileView(View):
    """
    Vue pour afficher "Mon profil enseignant".
    
    Affiche le profil de l'enseignant connecté.
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche le profil enseignant de l'utilisateur connecté.
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé.')
            return redirect('app_profile:login')
        
        # Vérifier si l'utilisateur est un enseignant
        if not hasattr(profile, 'teacher'):
            messages.error(request, 'Vous n\'êtes pas un enseignant.')
            return redirect('app_profile:profile_view')
        
        teacher = profile.teacher
        
        context = {
            'profile': profile,
            'teacher': teacher,
        }
        
        return render(request, 'app_profile/my_teacher_profile.html', context)


# ==================== PARENT CRUD ====================

class ParentListView(PermissionRequiredMixin, ListView):
    """
    Vue pour lister tous les parents.
    
    Requiert la permission: view_parent
    """
    model = Parent
    template_name = 'app_profile/parent_list.html'
    context_object_name = 'parents'
    paginate_by = 20
    required_permission = 'view_parent'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        """
        Récupère la liste des parents avec filtres.
        """
        queryset = Parent.get_active_parents()
        
        # Filtre par recherche
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(profile__full_name__icontains=search) |
                Q(parent_number__icontains=search) |
                Q(relationship_type__icontains=search)
            )
        
        # Filtre par type de relation
        relationship = self.request.GET.get('relationship', '')
        if relationship:
            queryset = queryset.filter(relationship_type=relationship)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['relationship_filter'] = self.request.GET.get('relationship', '')
        return context


class ParentDetailView(PermissionRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un parent (fiche parent).
    
    Requiert la permission: view_parent
    """
    model = Parent
    template_name = 'app_profile/parent_detail.html'
    context_object_name = 'parent'
    required_permission = 'view_parent'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Parent.get_active_parents()


class ParentCreateView(PermissionRequiredMixin, CreateView):
    """
    Vue pour créer un nouveau parent.
    
    Requiert la permission: create_parent
    """
    model = Parent
    form_class = ParentForm
    template_name = 'app_profile/parent_create.html'
    required_permission = 'create_parent'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les profils disponibles sans parent
        profiles_without_parent = Profile.objects.filter(
            is_active=True
        ).exclude(
            parent__isnull=False
        ).select_related('user')
        context['available_profiles'] = profiles_without_parent
        return context
    
    def form_valid(self, form):
        """
        Sauvegarde le parent et définit created_by.
        """
        form.instance.created_by = self.request.user
        # Récupérer le profil sélectionné
        profile_id = self.request.POST.get('profile_id')
        if profile_id:
            profile = get_object_or_404(Profile, id=profile_id, is_active=True)
            form.instance.profile = profile
            # Mettre à jour le rôle du profil
            profile.role = 'parent'
            profile.save()
            # Générer le numéro de parent si vide
            if not form.instance.parent_number:
                from .services.utils import generate_parent_number
                form.instance.parent_number = generate_parent_number()
        else:
            messages.error(self.request, 'Veuillez sélectionner un profil.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Parent créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_profile:parent_detail', kwargs={'pk': self.object.pk})


class ParentUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Vue pour modifier un parent existant.
    
    Requiert la permission: edit_parent
    """
    model = Parent
    form_class = ParentForm
    template_name = 'app_profile/parent_update.html'
    required_permission = 'edit_parent'
    required_resource = 'app_profile'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Parent.get_active_parents()
    
    def form_valid(self, form):
        """
        Sauvegarde le parent et définit updated_by.
        """
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Parent modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_profile:parent_detail', kwargs={'pk': self.object.pk})


class MyParentProfileView(View):
    """
    Vue pour afficher "Mon profil parent".
    
    Affiche le profil du parent connecté.
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche le profil parent de l'utilisateur connecté.
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé.')
            return redirect('app_profile:login')
        
        # Vérifier si l'utilisateur est un parent
        if not hasattr(profile, 'parent'):
            messages.error(request, 'Vous n\'êtes pas un parent.')
            return redirect('app_profile:profile_view')
        
        parent = profile.parent
        
        context = {
            'profile': profile,
            'parent': parent,
        }
        
        return render(request, 'app_profile/my_parent_profile.html', context)


# ==================== AUTRES VUES ====================

class PhotoUploadView(View):
    """
    Vue pour uploader une photo de profil.
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """
        Upload une photo de profil.
        """
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé.')
            return redirect('app_profile:profile_view')
        
        form = PhotoUploadForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Photo de profil mise à jour avec succès!')
        else:
            for error in form.errors.values():
                messages.error(request, error)
        
        return redirect('app_profile:profile_view')


class LoginHistoryView(View):
    """
    Vue pour afficher l'historique de connexion.
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche l'historique de connexion de l'utilisateur.
        """
        user = request.user
        
        # Récupérer l'historique (50 dernières entrées)
        login_history = LoginHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:50]
        
        context = {
            'login_history': login_history,
        }
        
        return render(request, 'app_profile/login_history.html', context)


class ActivityLogsView(View):
    """
    Vue pour afficher les logs d'activités du profil.
    """
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche les logs d'activités du profil.
        """
        user = request.user
        
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(request, 'Profil non trouvé.')
            return redirect('app_profile:profile_view')
        
        # Pour l'instant, on utilise l'historique de connexion
        # Dans une version future, on pourrait avoir un modèle ActivityLog dédié
        activity_logs = LoginHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:100]
        
        context = {
            'profile': profile,
            'activity_logs': activity_logs,
        }
        
        return render(request, 'app_profile/activity_logs.html', context)


class RolesManagementView(PermissionRequiredMixin, View):
    """
    Vue pour gérer les rôles et permissions.
    
    Requiert la permission: manage_roles
    """
    required_permission = 'manage_roles'
    required_resource = 'app_config'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche la page de gestion des rôles et permissions.
        """
        # Récupérer tous les rôles
        roles = Role.objects.filter(is_active=True).order_by('name')
        
        # Récupérer toutes les permissions
        permissions = Permission.objects.filter(is_active=True).order_by('resource', 'action', 'name')
        
        # Grouper les permissions par ressource
        permissions_by_resource = {}
        for perm in permissions:
            if perm.resource not in permissions_by_resource:
                permissions_by_resource[perm.resource] = []
            permissions_by_resource[perm.resource].append(perm)
        
        context = {
            'roles': roles,
            'permissions': permissions,
            'permissions_by_resource': permissions_by_resource,
        }
        
        return render(request, 'app_profile/roles_management.html', context)

