from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import (
    Profile, ParentProfile, Organisation,
    DocumentVerification, UserSession, LoginHistory,
    TrustedDevice, UserPreferences, Student, Teacher, Parent
)


@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Profile.
    """
    list_display = ['get_full_name', 'get_username', 'reference', 'phone', 'gender', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_verified', 'gender', 'country', 'created_at']
    search_fields = ['full_name', 'firstname', 'name', 'user__username', 'phone', 'id_card_number', 'reference']
    ordering = ['-created_at']
    readonly_fields = ['reference', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations personnelles', {
            'fields': ('full_name', 'firstname', 'name', 'birth_date', 'gender', 'id_card_number')
        }),
        ('Contact & Localisation', {
            'fields': ('phone', 'country')
        }),
        ('Rôle et Sécurité', {
            'fields': ('role', 'pincode')
        }),
        ('Statut', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Métadonnées', {
            'fields': ('reference', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        """Affiche le nom complet."""
        return obj.full_name
    get_full_name.short_description = 'Nom complet'
    get_full_name.admin_order_field = 'full_name'
    
    def get_username(self, obj):
        """Affiche le username."""
        return obj.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'

@admin.register(DocumentVerification)
class DocumentVerificationAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle DocumentVerification.
    """
    list_display = ['get_profile_name', 'get_username', 'document_type', 'get_status_display_colored', 'get_address_preview', 'verified_by', 'created_at']
    list_filter = ['status', 'document_type', 'created_at', 'verified_at']
    search_fields = ['profile__full_name', 'profile__user__username', 'address', 'profile__phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    raw_id_fields = ['profile', 'verified_by']
    
    fieldsets = (
        ('Profil', {
            'fields': ('profile',)
        }),
        ('Document', {
            'fields': ('document_type', 'document_front', 'document_back', 'selfie_photo', 'address')
        }),
        ('Statut de vérification', {
            'fields': ('status', 'verified_by', 'verified_at')
        }),
        ('Notes et commentaires', {
            'fields': ('admin_notes', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_selected', 'reject_selected', 'set_under_review']
    
    def get_profile_name(self, obj):
        """Affiche le nom du profil."""
        return obj.profile.full_name
    get_profile_name.short_description = 'Profil'
    get_profile_name.admin_order_field = 'profile__full_name'
    
    def get_username(self, obj):
        """Affiche le username."""
        return obj.profile.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'profile__user__username'
    
    def get_status_display_colored(self, obj):
        """Affiche le statut avec couleur."""
        colors = {
            'pending': 'orange',
            'under_review': 'blue',
            'approved': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_display_colored.short_description = 'Statut'
    get_status_display_colored.admin_order_field = 'status'
    
    def get_address_preview(self, obj):
        """Affiche un aperçu de l'adresse."""
        if obj.address:
            preview = obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
            return preview
        return '-'
    get_address_preview.short_description = 'Adresse'
    
    def approve_selected(self, request, queryset):
        """Approuve les documents sélectionnés."""
        count = 0
        for doc in queryset.filter(status__in=['pending', 'under_review']):
            doc.approve(request.user)
            count += 1
        self.message_user(request, f'{count} document(s) approuvé(s) avec succès.')
    approve_selected.short_description = 'Approuver les documents sélectionnés'
    
    def reject_selected(self, request, queryset):
        """Rejette les documents sélectionnés."""
        count = 0
        for doc in queryset.filter(status__in=['pending', 'under_review']):
            doc.reject(request.user, 'Rejeté par l\'administrateur')
            count += 1
        self.message_user(request, f'{count} document(s) rejeté(s).')
    reject_selected.short_description = 'Rejeter les documents sélectionnés'
    
    def set_under_review(self, request, queryset):
        """Marque les documents comme en cours de vérification."""
        count = queryset.filter(status='pending').update(status='under_review')
        self.message_user(request, f'{count} document(s) marqué(s) comme en cours de vérification.')
    set_under_review.short_description = 'Marquer comme en cours de vérification'


@admin.register(UserSession)
class UserSessionAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle UserSession.
    """
    list_display = ['get_username', 'device_name', 'ip_address', 'location', 'is_active', 'last_activity', 'created_at']
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__username', 'device_name', 'ip_address', 'location']
    ordering = ['-last_activity']
    readonly_fields = ['created_at', 'last_activity']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Session', {
            'fields': ('session_key', 'is_active')
        }),
        ('Appareil', {
            'fields': ('device_name', 'user_agent', 'ip_address', 'location')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    def get_username(self, obj):
        """Affiche le username."""
        return obj.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'


@admin.register(LoginHistory)
class LoginHistoryAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle LoginHistory.
    """
    list_display = ['username', 'get_user_display', 'get_status_display_colored', 'ip_address', 'device_name', 'location', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['username', 'user__username', 'ip_address', 'device_name', 'location']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'username')
        }),
        ('Statut', {
            'fields': ('status', 'failure_reason')
        }),
        ('Connexion', {
            'fields': ('ip_address', 'user_agent', 'device_name', 'location')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_display(self, obj):
        """Affiche l'utilisateur ou 'N/A'."""
        if obj.user:
            return obj.user.username
        return format_html('<span style="color: gray;">N/A</span>')
    get_user_display.short_description = 'Utilisateur'
    get_user_display.admin_order_field = 'user__username'
    
    def get_status_display_colored(self, obj):
        """Affiche le statut avec couleur."""
        colors = {
            'success': 'green',
            'failed': 'red',
            'blocked': 'darkred'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_display_colored.short_description = 'Statut'
    get_status_display_colored.admin_order_field = 'status'


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle TrustedDevice.
    """
    list_display = ['get_username', 'device_name', 'ip_address', 'location', 'is_active', 'last_used', 'created_at']
    list_filter = ['is_active', 'created_at', 'last_used']
    search_fields = ['user__username', 'device_name', 'ip_address', 'device_fingerprint', 'location']
    ordering = ['-last_used']
    readonly_fields = ['created_at', 'last_used', 'device_fingerprint']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Appareil', {
            'fields': ('device_name', 'device_fingerprint', 'is_active')
        }),
        ('Informations de connexion', {
            'fields': ('ip_address', 'user_agent', 'location')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'last_used'),
            'classes': ('collapse',)
        }),
    )
    
    def get_username(self, obj):
        """Affiche le username."""
        return obj.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'


@admin.register(UserPreferences)
class UserPreferencesAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle UserPreferences.
    """
    list_display = ['get_profile_name', 'get_username', 'language', 'theme', 'timezone', 'email_notifications', 'created_at']
    list_filter = ['language', 'theme', 'email_notifications', 'sms_notifications', 'push_notifications', 'created_at']
    search_fields = ['profile__full_name', 'profile__user__username', 'timezone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['profile']
    
    fieldsets = (
        ('Profil', {
            'fields': ('profile',)
        }),
        ('Langue et Localisation', {
            'fields': ('language', 'timezone')
        }),
        ('Notifications', {
            'fields': (
                'email_notifications', 'sms_notifications', 'push_notifications',
                'transaction_notifications', 'security_notifications'
            )
        }),
        ('Affichage', {
            'fields': ('theme', 'items_per_page')
        }),
        ('Confidentialité', {
            'fields': ('profile_visibility', 'show_email', 'show_phone', 'allow_search')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_profile_name(self, obj):
        """Affiche le nom du profil."""
        return obj.profile.full_name
    get_profile_name.short_description = 'Profil'
    get_profile_name.admin_order_field = 'profile__full_name'
    
    def get_username(self, obj):
        """Affiche le username."""
        return obj.profile.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'profile__user__username'


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Student.
    """
    list_display = ['get_full_name', 'get_username', 'student_number', 'class_level', 'enrollment_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'class_level', 'enrollment_date', 'created_at']
    search_fields = ['profile__full_name', 'profile__user__username', 'student_number', 'class_level']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['profile', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Profil', {
            'fields': ('profile',)
        }),
        ('Informations élève', {
            'fields': ('student_number', 'enrollment_date', 'class_level')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        """Affiche le nom complet."""
        return obj.profile.full_name
    get_full_name.short_description = 'Nom complet'
    get_full_name.admin_order_field = 'profile__full_name'
    
    def get_username(self, obj):
        """Affiche le username."""
        return obj.profile.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'profile__user__username'


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Teacher.
    """
    list_display = ['get_full_name', 'get_username', 'teacher_number', 'specialization', 'department', 'hire_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'specialization', 'hire_date', 'created_at']
    search_fields = ['profile__full_name', 'profile__user__username', 'teacher_number', 'specialization', 'department']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['profile', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Profil', {
            'fields': ('profile',)
        }),
        ('Informations enseignant', {
            'fields': ('teacher_number', 'hire_date', 'specialization', 'department')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        """Affiche le nom complet."""
        return obj.profile.full_name
    get_full_name.short_description = 'Nom complet'
    get_full_name.admin_order_field = 'profile__full_name'
    
    def get_username(self, obj):
        """Affiche le username."""
        return obj.profile.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'profile__user__username'


@admin.register(Parent)
class ParentAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Parent.
    """
    list_display = ['get_full_name', 'get_username', 'parent_number', 'relationship_type', 'occupation', 'emergency_contact', 'is_active', 'created_at']
    list_filter = ['is_active', 'relationship_type', 'emergency_contact', 'created_at']
    search_fields = ['profile__full_name', 'profile__user__username', 'parent_number', 'relationship_type', 'occupation']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['profile', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Profil', {
            'fields': ('profile',)
        }),
        ('Informations parent', {
            'fields': ('parent_number', 'relationship_type', 'occupation', 'emergency_contact')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        """Affiche le nom complet."""
        return obj.profile.full_name
    get_full_name.short_description = 'Nom complet'
    get_full_name.admin_order_field = 'profile__full_name'
    
    def get_username(self, obj):
        """Affiche le username."""
        return obj.profile.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'profile__user__username'
