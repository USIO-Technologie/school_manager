"""
Vues pour l'application app_grades.

Ce module contient les vues Django pour la gestion des notes.
"""

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy

from .models import GradeScale, GradeCategory, Assessment, StudentGrade, ReportCard
from app_config.permissions import PermissionRequiredMixin


# ==================== GRADE SCALE ====================

class GradeScaleListView(PermissionRequiredMixin, ListView):
    model = GradeScale
    template_name = 'app_grades/grade_scale_list.html'
    context_object_name = 'grade_scales'
    paginate_by = 20
    required_permission = 'view_grade'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = GradeScale.objects.filter(is_active=True).order_by('name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        return queryset


# ==================== GRADE CATEGORY ====================

class GradeCategoryListView(PermissionRequiredMixin, ListView):
    model = GradeCategory
    template_name = 'app_grades/grade_category_list.html'
    context_object_name = 'grade_categories'
    paginate_by = 20
    required_permission = 'view_assessment'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = GradeCategory.objects.filter(is_active=True).order_by('name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return queryset


# ==================== ASSESSMENT ====================

class AssessmentListView(PermissionRequiredMixin, ListView):
    model = Assessment
    template_name = 'app_grades/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20
    required_permission = 'view_assessment'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = Assessment.objects.filter(is_active=True).select_related('subject', 'class_section', 'category', 'academic_year').order_by('-date', 'subject', 'class_section')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(subject__name__icontains=search))
        return queryset


# ==================== STUDENT GRADE ====================

class StudentGradeListView(PermissionRequiredMixin, ListView):
    model = StudentGrade
    template_name = 'app_grades/student_grade_list.html'
    context_object_name = 'student_grades'
    paginate_by = 20
    required_permission = 'view_grade'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = StudentGrade.objects.filter(is_active=True).select_related('student', 'student__profile', 'assessment').order_by('-assessment__date', 'student')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(student__profile__full_name__icontains=search) | Q(assessment__name__icontains=search))
        return queryset


# ==================== REPORT CARD ====================

class ReportCardListView(PermissionRequiredMixin, ListView):
    model = ReportCard
    template_name = 'app_grades/report_card_list.html'
    context_object_name = 'report_cards'
    paginate_by = 20
    required_permission = 'view_report_card'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        queryset = ReportCard.objects.filter(is_active=True).select_related('student', 'student__profile', 'academic_year').order_by('-academic_year', 'student', '-term')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(student__profile__full_name__icontains=search) | Q(term__icontains=search))
        return queryset


# ==================== GRADE CATEGORY CRUD ====================

class GradeCategoryDetailView(PermissionRequiredMixin, DetailView):
    model = GradeCategory
    template_name = 'app_grades/grade_category_detail.html'
    context_object_name = 'grade_category'
    required_permission = 'view_assessment'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return GradeCategory.objects.filter(is_active=True)


class GradeCategoryCreateView(PermissionRequiredMixin, CreateView):
    model = GradeCategory
    template_name = 'app_grades/grade_category_create.html'
    fields = ['name', 'code', 'weight', 'description', 'is_active']
    required_permission = 'create_assessment'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Catégorie créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:grade_category_detail', kwargs={'pk': self.object.pk})


class GradeCategoryUpdateView(PermissionRequiredMixin, UpdateView):
    model = GradeCategory
    template_name = 'app_grades/grade_category_update.html'
    fields = ['name', 'code', 'weight', 'description', 'is_active']
    required_permission = 'edit_assessment'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return GradeCategory.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Catégorie modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:grade_category_detail', kwargs={'pk': self.object.pk})


# ==================== ASSESSMENT CRUD ====================

class AssessmentDetailView(PermissionRequiredMixin, DetailView):
    model = Assessment
    template_name = 'app_grades/assessment_detail.html'
    context_object_name = 'assessment'
    required_permission = 'view_assessment'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Assessment.objects.filter(is_active=True).select_related('subject', 'class_section', 'category', 'academic_year')


class AssessmentCreateView(PermissionRequiredMixin, CreateView):
    model = Assessment
    template_name = 'app_grades/assessment_create.html'
    fields = ['name', 'subject', 'class_section', 'category', 'date', 'coefficient', 'max_score', 'academic_year', 'description', 'is_active']
    required_permission = 'create_assessment'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Évaluation créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:assessment_detail', kwargs={'pk': self.object.pk})


class AssessmentUpdateView(PermissionRequiredMixin, UpdateView):
    model = Assessment
    template_name = 'app_grades/assessment_update.html'
    fields = ['name', 'subject', 'class_section', 'category', 'date', 'coefficient', 'max_score', 'academic_year', 'description', 'is_active']
    required_permission = 'edit_assessment'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return Assessment.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Évaluation modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:assessment_detail', kwargs={'pk': self.object.pk})


# ==================== STUDENT GRADE CRUD ====================

class StudentGradeDetailView(PermissionRequiredMixin, DetailView):
    model = StudentGrade
    template_name = 'app_grades/student_grade_detail.html'
    context_object_name = 'student_grade'
    required_permission = 'view_grade'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return StudentGrade.objects.filter(is_active=True).select_related('student', 'student__profile', 'assessment', 'assessment__subject', 'assessment__class_section')


class StudentGradeCreateView(PermissionRequiredMixin, CreateView):
    model = StudentGrade
    template_name = 'app_grades/student_grade_create.html'
    fields = ['student', 'assessment', 'score', 'is_absent', 'comment', 'is_active']
    required_permission = 'create_grade'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Note créée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:student_grade_detail', kwargs={'pk': self.object.pk})


class StudentGradeUpdateView(PermissionRequiredMixin, UpdateView):
    model = StudentGrade
    template_name = 'app_grades/student_grade_update.html'
    fields = ['student', 'assessment', 'score', 'is_absent', 'comment', 'is_active']
    required_permission = 'edit_grade'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return StudentGrade.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Note modifiée avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:student_grade_detail', kwargs={'pk': self.object.pk})


# ==================== REPORT CARD CRUD ====================

class ReportCardDetailView(PermissionRequiredMixin, DetailView):
    model = ReportCard
    template_name = 'app_grades/report_card_detail.html'
    context_object_name = 'report_card'
    required_permission = 'view_report_card'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return ReportCard.objects.filter(is_active=True).select_related('student', 'student__profile', 'academic_year')


class ReportCardCreateView(PermissionRequiredMixin, CreateView):
    model = ReportCard
    template_name = 'app_grades/report_card_create.html'
    fields = ['student', 'academic_year', 'term', 'overall_average', 'rank', 'total_students', 'comments', 'is_active']
    required_permission = 'create_report_card'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Bulletin créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:report_card_detail', kwargs={'pk': self.object.pk})


class ReportCardUpdateView(PermissionRequiredMixin, UpdateView):
    model = ReportCard
    template_name = 'app_grades/report_card_update.html'
    fields = ['student', 'academic_year', 'term', 'overall_average', 'rank', 'total_students', 'comments', 'is_active']
    required_permission = 'edit_report_card'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return ReportCard.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Bulletin modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:report_card_detail', kwargs={'pk': self.object.pk})


# ==================== GRADE SCALE CRUD ====================

class GradeScaleDetailView(PermissionRequiredMixin, DetailView):
    model = GradeScale
    template_name = 'app_grades/grade_scale_detail.html'
    context_object_name = 'grade_scale'
    required_permission = 'view_grade'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return GradeScale.objects.filter(is_active=True)


class GradeScaleCreateView(PermissionRequiredMixin, CreateView):
    model = GradeScale
    template_name = 'app_grades/grade_scale_create.html'
    fields = ['name', 'min_score', 'max_score', 'passing_score', 'description', 'is_active']
    required_permission = 'create_grade'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Barème créé avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:grade_scale_detail', kwargs={'pk': self.object.pk})


class GradeScaleUpdateView(PermissionRequiredMixin, UpdateView):
    model = GradeScale
    template_name = 'app_grades/grade_scale_update.html'
    fields = ['name', 'min_score', 'max_score', 'passing_score', 'description', 'is_active']
    required_permission = 'edit_grade'
    required_resource = 'app_grades'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return GradeScale.objects.filter(is_active=True)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Barème modifié avec succès!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app_grades:grade_scale_detail', kwargs={'pk': self.object.pk})
