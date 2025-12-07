"""
Vues pour l'application app_attendance.

Ce module contient les vues Django pour la gestion des présences.
"""

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy

from .models import AttendanceRule, Attendance, Absence, Excuse
from app_config.permissions import PermissionRequiredMixin


# ==================== ATTENDANCE RULE ====================

class AttendanceRuleListView(PermissionRequiredMixin, ListView):
    model = AttendanceRule
    template_name = 'app_attendance/attendance_rule_list.html'
    context_object_name = 'attendance_rules'
    paginate_by = 20
    required_permission = 'view_attendance'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = AttendanceRule.objects.filter(is_active=True).order_by('name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        return queryset


# ==================== ATTENDANCE ====================

class AttendanceListView(PermissionRequiredMixin, ListView):
    model = Attendance
    template_name = 'app_attendance/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 20
    required_permission = 'view_attendance'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Attendance.objects.filter(is_active=True).select_related('student', 'student__profile', 'class_section').order_by('-date', 'student')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(student__profile__full_name__icontains=search) | Q(class_section__name__icontains=search))
        return queryset


# ==================== ABSENCE ====================

class AbsenceListView(PermissionRequiredMixin, ListView):
    model = Absence
    template_name = 'app_attendance/absence_list.html'
    context_object_name = 'absences'
    paginate_by = 20
    required_permission = 'view_absence'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Absence.objects.filter(is_active=True).select_related('student', 'student__profile', 'justified_by', 'justified_by__profile').order_by('-start_date', 'student')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(student__profile__full_name__icontains=search) | Q(reason__icontains=search))
        return queryset


# ==================== EXCUSE ====================

class ExcuseListView(PermissionRequiredMixin, ListView):
    model = Excuse
    template_name = 'app_attendance/excuse_list.html'
    context_object_name = 'excuses'
    paginate_by = 20
    required_permission = 'view_excuse'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Excuse.objects.filter(is_active=True).select_related('absence', 'absence__student', 'absence__student__profile').order_by('-created_at')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(absence__student__profile__full_name__icontains=search) | Q(reason__icontains=search))
        return queryset


# ==================== ATTENDANCE RULE CRUD ====================

class AttendanceRuleDetailView(PermissionRequiredMixin, DetailView):
    model = AttendanceRule
    template_name = 'app_attendance/attendance_rule_detail.html'
    context_object_name = 'attendance_rule'
    required_permission = 'view_attendance'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return AttendanceRule.objects.filter(is_active=True)


class AttendanceRuleCreateView(PermissionRequiredMixin, CreateView):
    model = AttendanceRule
    template_name = 'app_attendance/attendance_rule_create.html'
    fields = ['name', 'max_absences', 'alert_threshold', 'period_days', 'description', 'is_active']
    required_permission = 'create_attendance'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Règle créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_attendance:attendance_rule_detail', kwargs={'pk': self.object.pk})


class AttendanceRuleUpdateView(PermissionRequiredMixin, UpdateView):
    model = AttendanceRule
    template_name = 'app_attendance/attendance_rule_update.html'
    fields = ['name', 'max_absences', 'alert_threshold', 'period_days', 'description', 'is_active']
    required_permission = 'edit_attendance'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return AttendanceRule.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Règle modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_attendance:attendance_rule_detail', kwargs={'pk': self.object.pk})


# ==================== ATTENDANCE CRUD ====================

class AttendanceDetailView(PermissionRequiredMixin, DetailView):
    model = Attendance
    template_name = 'app_attendance/attendance_detail.html'
    context_object_name = 'attendance'
    required_permission = 'view_attendance'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Attendance.objects.filter(is_active=True).select_related('student', 'student__profile', 'class_section')


class AttendanceCreateView(PermissionRequiredMixin, CreateView):
    model = Attendance
    template_name = 'app_attendance/attendance_create.html'
    fields = ['student', 'class_section', 'date', 'status', 'time_in', 'time_out', 'notes', 'is_active']
    required_permission = 'create_attendance'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Présence créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_attendance:attendance_detail', kwargs={'pk': self.object.pk})


class AttendanceUpdateView(PermissionRequiredMixin, UpdateView):
    model = Attendance
    template_name = 'app_attendance/attendance_update.html'
    fields = ['student', 'class_section', 'date', 'status', 'time_in', 'time_out', 'notes', 'is_active']
    required_permission = 'edit_attendance'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Attendance.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Présence modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_attendance:attendance_detail', kwargs={'pk': self.object.pk})


# ==================== ABSENCE CRUD ====================

class AbsenceDetailView(PermissionRequiredMixin, DetailView):
    model = Absence
    template_name = 'app_attendance/absence_detail.html'
    context_object_name = 'absence'
    required_permission = 'view_absence'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Absence.objects.filter(is_active=True).select_related('student', 'student__profile', 'justified_by', 'justified_by__profile')


class AbsenceCreateView(PermissionRequiredMixin, CreateView):
    model = Absence
    template_name = 'app_attendance/absence_create.html'
    fields = ['student', 'start_date', 'end_date', 'reason', 'is_justified', 'is_active']
    required_permission = 'create_absence'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Absence créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_attendance:absence_detail', kwargs={'pk': self.object.pk})


class AbsenceUpdateView(PermissionRequiredMixin, UpdateView):
    model = Absence
    template_name = 'app_attendance/absence_update.html'
    fields = ['student', 'start_date', 'end_date', 'reason', 'is_justified', 'is_active']
    required_permission = 'edit_absence'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Absence.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Absence modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_attendance:absence_detail', kwargs={'pk': self.object.pk})


# ==================== EXCUSE CRUD ====================

class ExcuseDetailView(PermissionRequiredMixin, DetailView):
    model = Excuse
    template_name = 'app_attendance/excuse_detail.html'
    context_object_name = 'excuse'
    required_permission = 'view_excuse'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Excuse.objects.filter(is_active=True).select_related('absence', 'absence__student', 'absence__student__profile', 'reviewed_by')


class ExcuseCreateView(PermissionRequiredMixin, CreateView):
    model = Excuse
    template_name = 'app_attendance/excuse_create.html'
    fields = ['absence', 'reason', 'document', 'status']
    required_permission = 'create_excuse'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Justificatif créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_attendance:excuse_detail', kwargs={'pk': self.object.pk})


class ExcuseUpdateView(PermissionRequiredMixin, UpdateView):
    model = Excuse
    template_name = 'app_attendance/excuse_update.html'
    fields = ['absence', 'reason', 'document', 'status']
    required_permission = 'edit_excuse'
    required_resource = 'app_attendance'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Excuse.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Justificatif modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_attendance:excuse_detail', kwargs={'pk': self.object.pk})
