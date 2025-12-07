"""
Vues pour l'application app_academic.

Ce module contient les vues Django pour la gestion académique.
"""

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy
from django.forms import ModelForm

from .models import AcademicYear, Grade, ClassRoom, Class, Subject, Course, Schedule
from app_config.permissions import PermissionRequiredMixin


# ==================== ACADEMIC YEAR ====================

class AcademicYearListView(PermissionRequiredMixin, ListView):
    model = AcademicYear
    template_name = 'app_academic/academic_year_list.html'
    context_object_name = 'academic_years'
    paginate_by = 20
    required_permission = 'view_academic_year'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = AcademicYear.objects.filter(is_active=True).order_by('-start_date')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        return queryset


# ==================== GRADE ====================

class GradeListView(PermissionRequiredMixin, ListView):
    model = Grade
    template_name = 'app_academic/grade_list.html'
    context_object_name = 'grades'
    paginate_by = 20
    required_permission = 'view_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Grade.objects.filter(is_active=True).order_by('order', 'name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return queryset


# ==================== CLASSROOM ====================

class ClassroomListView(PermissionRequiredMixin, ListView):
    model = ClassRoom
    template_name = 'app_academic/classroom_list.html'
    context_object_name = 'classrooms'
    paginate_by = 20
    required_permission = 'view_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = ClassRoom.objects.filter(is_active=True).order_by('name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        return queryset


# ==================== CLASS ====================

class ClassListView(PermissionRequiredMixin, ListView):
    model = Class
    template_name = 'app_academic/class_list.html'
    context_object_name = 'classes'
    paginate_by = 20
    required_permission = 'view_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Class.objects.filter(is_active=True).select_related('grade', 'academic_year', 'classroom', 'teacher').order_by('academic_year', 'grade__order', 'name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return queryset


# ==================== SUBJECT ====================

class SubjectListView(PermissionRequiredMixin, ListView):
    model = Subject
    template_name = 'app_academic/subject_list.html'
    context_object_name = 'subjects'
    paginate_by = 20
    required_permission = 'view_subject'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Subject.objects.filter(is_active=True).order_by('name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return queryset


# ==================== COURSE ====================

class CourseListView(PermissionRequiredMixin, ListView):
    model = Course
    template_name = 'app_academic/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20
    required_permission = 'view_academic_year'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True).select_related('subject', 'class_section', 'teacher', 'academic_year').order_by('academic_year', 'class_section', 'subject')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(subject__name__icontains=search) | Q(class_section__name__icontains=search))
        return queryset


# ==================== SCHEDULE ====================

class ScheduleListView(PermissionRequiredMixin, ListView):
    model = Schedule
    template_name = 'app_academic/schedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 20
    required_permission = 'view_schedule'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Schedule.objects.filter(is_active=True).select_related('course', 'course__subject', 'course__class_section', 'classroom').order_by('day_of_week', 'start_time')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(course__subject__name__icontains=search) | Q(course__class_section__name__icontains=search))
        return queryset


# ==================== ACADEMIC YEAR CRUD ====================

class AcademicYearDetailView(PermissionRequiredMixin, DetailView):
    model = AcademicYear
    template_name = 'app_academic/academic_year_detail.html'
    context_object_name = 'academic_year'
    required_permission = 'view_academic_year'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return AcademicYear.objects.filter(is_active=True)


class AcademicYearCreateView(PermissionRequiredMixin, CreateView):
    model = AcademicYear
    template_name = 'app_academic/academic_year_create.html'
    fields = ['name', 'start_date', 'end_date', 'is_current', 'is_active']
    required_permission = 'create_academic_year'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Année scolaire créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:academic_year_detail', kwargs={'pk': self.object.pk})


class AcademicYearUpdateView(PermissionRequiredMixin, UpdateView):
    model = AcademicYear
    template_name = 'app_academic/academic_year_update.html'
    fields = ['name', 'start_date', 'end_date', 'is_current', 'is_active']
    required_permission = 'edit_academic_year'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return AcademicYear.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Année scolaire modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:academic_year_detail', kwargs={'pk': self.object.pk})


# ==================== GRADE CRUD ====================

class GradeDetailView(PermissionRequiredMixin, DetailView):
    model = Grade
    template_name = 'app_academic/grade_detail.html'
    context_object_name = 'grade'
    required_permission = 'view_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Grade.objects.filter(is_active=True)


class GradeCreateView(PermissionRequiredMixin, CreateView):
    model = Grade
    template_name = 'app_academic/grade_create.html'
    fields = ['name', 'code', 'order', 'description', 'is_active']
    required_permission = 'create_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Niveau créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:grade_detail', kwargs={'pk': self.object.pk})


class GradeUpdateView(PermissionRequiredMixin, UpdateView):
    model = Grade
    template_name = 'app_academic/grade_update.html'
    fields = ['name', 'code', 'order', 'description', 'is_active']
    required_permission = 'edit_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Grade.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Niveau modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:grade_detail', kwargs={'pk': self.object.pk})


# ==================== CLASSROOM CRUD ====================

class ClassroomDetailView(PermissionRequiredMixin, DetailView):
    model = ClassRoom
    template_name = 'app_academic/classroom_detail.html'
    context_object_name = 'classroom'
    required_permission = 'view_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return ClassRoom.objects.filter(is_active=True)


class ClassroomCreateView(PermissionRequiredMixin, CreateView):
    model = ClassRoom
    template_name = 'app_academic/classroom_create.html'
    fields = ['name', 'capacity', 'floor', 'equipment', 'is_active']
    required_permission = 'create_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Salle créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:classroom_detail', kwargs={'pk': self.object.pk})


class ClassroomUpdateView(PermissionRequiredMixin, UpdateView):
    model = ClassRoom
    template_name = 'app_academic/classroom_update.html'
    fields = ['name', 'capacity', 'floor', 'equipment', 'is_active']
    required_permission = 'edit_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return ClassRoom.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Salle modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:classroom_detail', kwargs={'pk': self.object.pk})


# ==================== CLASS CRUD ====================

class ClassDetailView(PermissionRequiredMixin, DetailView):
    model = Class
    template_name = 'app_academic/class_detail.html'
    context_object_name = 'class_obj'
    required_permission = 'view_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Class.objects.filter(is_active=True).select_related('grade', 'academic_year', 'classroom', 'teacher')


class ClassCreateView(PermissionRequiredMixin, CreateView):
    model = Class
    template_name = 'app_academic/class_create.html'
    fields = ['name', 'code', 'grade', 'academic_year', 'classroom', 'capacity', 'teacher', 'is_active']
    required_permission = 'create_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Classe créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:class_detail', kwargs={'pk': self.object.pk})


class ClassUpdateView(PermissionRequiredMixin, UpdateView):
    model = Class
    template_name = 'app_academic/class_update.html'
    fields = ['name', 'code', 'grade', 'academic_year', 'classroom', 'capacity', 'teacher', 'is_active']
    required_permission = 'edit_class'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Class.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Classe modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:class_detail', kwargs={'pk': self.object.pk})


# ==================== SUBJECT CRUD ====================

class SubjectDetailView(PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'app_academic/subject_detail.html'
    context_object_name = 'subject'
    required_permission = 'view_subject'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Subject.objects.filter(is_active=True)


class SubjectCreateView(PermissionRequiredMixin, CreateView):
    model = Subject
    template_name = 'app_academic/subject_create.html'
    fields = ['name', 'code', 'coefficient', 'description', 'is_active']
    required_permission = 'create_subject'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Matière créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:subject_detail', kwargs={'pk': self.object.pk})


class SubjectUpdateView(PermissionRequiredMixin, UpdateView):
    model = Subject
    template_name = 'app_academic/subject_update.html'
    fields = ['name', 'code', 'coefficient', 'description', 'is_active']
    required_permission = 'edit_subject'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Subject.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Matière modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:subject_detail', kwargs={'pk': self.object.pk})


# ==================== COURSE CRUD ====================

class CourseDetailView(PermissionRequiredMixin, DetailView):
    model = Course
    template_name = 'app_academic/course_detail.html'
    context_object_name = 'course'
    required_permission = 'view_academic_year'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Course.objects.filter(is_active=True).select_related('subject', 'class_section', 'teacher', 'academic_year')


class CourseCreateView(PermissionRequiredMixin, CreateView):
    model = Course
    template_name = 'app_academic/course_create.html'
    fields = ['subject', 'class_section', 'teacher', 'academic_year', 'is_active']
    required_permission = 'create_academic_year'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Cours créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:course_detail', kwargs={'pk': self.object.pk})


class CourseUpdateView(PermissionRequiredMixin, UpdateView):
    model = Course
    template_name = 'app_academic/course_update.html'
    fields = ['subject', 'class_section', 'teacher', 'academic_year', 'is_active']
    required_permission = 'edit_academic_year'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Course.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Cours modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:course_detail', kwargs={'pk': self.object.pk})


# ==================== SCHEDULE CRUD ====================

class ScheduleDetailView(PermissionRequiredMixin, DetailView):
    model = Schedule
    template_name = 'app_academic/schedule_detail.html'
    context_object_name = 'schedule'
    required_permission = 'view_schedule'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Schedule.objects.filter(is_active=True).select_related('course', 'course__subject', 'course__teacher', 'classroom')


class ScheduleCreateView(PermissionRequiredMixin, CreateView):
    model = Schedule
    template_name = 'app_academic/schedule_create.html'
    fields = ['course', 'day_of_week', 'start_time', 'end_time', 'classroom', 'is_active']
    required_permission = 'create_schedule'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Créneau créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:schedule_detail', kwargs={'pk': self.object.pk})


class ScheduleUpdateView(PermissionRequiredMixin, UpdateView):
    model = Schedule
    template_name = 'app_academic/schedule_update.html'
    fields = ['course', 'day_of_week', 'start_time', 'end_time', 'classroom', 'is_active']
    required_permission = 'edit_schedule'
    required_resource = 'app_academic'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Schedule.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Créneau modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_academic:schedule_detail', kwargs={'pk': self.object.pk})
