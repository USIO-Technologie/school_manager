"""
Configuration des URLs pour l'application app_profile.
Ce module contient les routes API pour l'authentification et la gestion des profils.
"""

from django.urls import path

from .views_landing import LandingPageView
from .views import (
    LoginView, DashboardRedirectView, StandardDashboardView, WebLoginView, LogoutView,
    ProfileView, ProfileUpdateView, ChangePasswordView, ProfileVerificationView,
    VerificationManagementView, VerificationDetailView, ProfileRolesManagementView,
    SecurityView, SettingsView, PasswordResetRequestView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from .views_crud import (
    ProfileListView, ProfileDetailView, ProfileCreateView, ProfileAdminUpdateView,
    StudentListView, StudentDetailView, StudentCreateView, StudentUpdateView, MyStudentProfileView,
    TeacherListView, TeacherDetailView, TeacherCreateView, TeacherUpdateView, MyTeacherProfileView,
    ParentListView, ParentDetailView, ParentCreateView, ParentUpdateView, MyParentProfileView,
    PhotoUploadView, LoginHistoryView, ActivityLogsView, RolesManagementView
)

app_name = 'app_profile'

urlpatterns = [
    # Landing page
    path('landing/', LandingPageView.as_view(), name='landing'),
    # Vues web
    path('login/', LoginView.as_view(), name='login'),
    path('login/ajax/', WebLoginView.as_view(), name='login_ajax'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardRedirectView.as_view(), name='dashboard_redirect'),
    path('dashboard/standard/', StandardDashboardView.as_view(), name='standard_dashboard'),
    path('profile/', ProfileView.as_view(), name='profile_view'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/verification/', ProfileVerificationView.as_view(), name='profile_verification'),
    path('profile/<int:profile_id>/roles/', ProfileRolesManagementView.as_view(), name='profile_roles_management'),
    path('profile/security/', SecurityView.as_view(), name='security'),
    path('profile/settings/', SettingsView.as_view(), name='settings'),
    path('verifications/', VerificationManagementView.as_view(), name='verification_management'),
    path('verifications/<int:verification_id>/', VerificationDetailView.as_view(), name='verification_detail'),
    
    # Password Reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Profile CRUD
    path('profiles/', ProfileListView.as_view(), name='profile_list'),
    path('profiles/create/', ProfileCreateView.as_view(), name='profile_create'),
    path('profiles/<int:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profiles/<int:pk>/update/', ProfileAdminUpdateView.as_view(), name='profile_admin_update'),
    
    # Student CRUD
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/create/', StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('my-student-profile/', MyStudentProfileView.as_view(), name='my_student_profile'),
    
    # Teacher CRUD
    path('teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/', TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/<int:pk>/update/', TeacherUpdateView.as_view(), name='teacher_update'),
    path('my-teacher-profile/', MyTeacherProfileView.as_view(), name='my_teacher_profile'),
    
    # Parent CRUD
    path('parents/', ParentListView.as_view(), name='parent_list'),
    path('parents/create/', ParentCreateView.as_view(), name='parent_create'),
    path('parents/<int:pk>/', ParentDetailView.as_view(), name='parent_detail'),
    path('parents/<int:pk>/update/', ParentUpdateView.as_view(), name='parent_update'),
    path('my-parent-profile/', MyParentProfileView.as_view(), name='my_parent_profile'),
    
    # Other views
    path('profile/upload-photo/', PhotoUploadView.as_view(), name='photo_upload'),
    path('profile/login-history/', LoginHistoryView.as_view(), name='login_history'),
    path('profile/activity-logs/', ActivityLogsView.as_view(), name='activity_logs'),
    path('roles-management/', RolesManagementView.as_view(), name='roles_management'),
    
    # Authentification API
]

