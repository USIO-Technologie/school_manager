"""
Context processors pour app_config.

Ces processeurs ajoutent des variables au contexte de tous les templates,
permettant d'accéder aux permissions et rôles de l'utilisateur.
"""

from django.urls import reverse, NoReverseMatch
from .permissions import has_permission, is_admin, get_user_permissions


def user_permissions(request):
    """
    Context processor qui ajoute les permissions de l'utilisateur au contexte.
    
    Ajoute les variables suivantes au contexte :
    - user_permissions: Liste des permissions de l'utilisateur
    - user_is_admin: Boolean indiquant si l'utilisateur est admin
    - has_permission: Fonction pour vérifier une permission spécifique
    """
    context = {
        'user_permissions': [],
        'user_is_admin': False,
        'has_permission': lambda perm, resource=None: False,
    }
    
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        try:
            profile = request.user.profile
            if profile and profile.is_active:
                # Récupérer toutes les permissions de l'utilisateur
                permissions = get_user_permissions(profile)
                context['user_permissions'] = [p.codename for p in permissions]
                
                # Vérifier si l'utilisateur est admin
                context['user_is_admin'] = is_admin(profile)
                
                # Fonction pour vérifier une permission
                def check_permission(permission_codename, resource=None):
                    return has_permission(profile, permission_codename, resource)
                
                context['has_permission'] = check_permission
        except Exception:
            # En cas d'erreur, on retourne les valeurs par défaut
            pass
    
    return context


def navigation_menu(request):
    """
    Context processor qui génère dynamiquement les menus du sidebar et navbar.
    
    Ajoute les variables suivantes au contexte :
    - sidebar_menu: Liste des menus du sidebar filtrés selon les permissions
    - user_profile: Profil de l'utilisateur connecté (pour navbar)
    - user_full_name: Nom complet de l'utilisateur
    - user_photo: Photo de profil de l'utilisateur
    """
    context = {
        'sidebar_menu': [],
        'user_profile': None,
        'user_full_name': None,
        'user_photo': None,
    }
    
    if not request.user.is_authenticated:
        return context
    
    # Récupérer le profil de l'utilisateur
    if not hasattr(request.user, 'profile'):
        return context
    
    try:
        profile = request.user.profile
        if not profile or not profile.is_active:
            return context
        
        context['user_profile'] = profile
        context['user_full_name'] = profile.full_name or request.user.get_full_name() or request.user.username
        context['user_photo'] = profile.photo if profile.photo else None
        
        # Fonction helper pour vérifier les permissions
        def check_perm(permission_codename, resource=None):
            return has_permission(profile, permission_codename, resource)
        
        # Fonction helper pour vérifier si un menu doit être affiché
        def should_show_menu(menu_item):
            # Si pas de permission requise, afficher pour tous les utilisateurs connectés
            if not menu_item.get('permission'):
                return True
            
            # Vérifier la permission
            resource = menu_item.get('resource', None)
            return check_perm(menu_item['permission'], resource)
        
        # Construire le menu du sidebar
        sidebar_menu_items = []
        
        # ========== DASHBOARD ==========
        dashboard_item = {
            'title': 'Dashboard',
            'icon': 'iconoir-home-simple',
            'url_name': 'app_profile:standard_dashboard',
            'permission': None,
            'resource': None,
            'children': [],
            'is_active': False,
        }
        try:
            dashboard_item['url'] = reverse('app_profile:standard_dashboard')
            if request.path.startswith('/profiles/dashboard/'):
                dashboard_item['is_active'] = True
        except NoReverseMatch:
            dashboard_item['url'] = '#'
        
        if should_show_menu(dashboard_item):
            sidebar_menu_items.append(dashboard_item)
        
        # ========== PROFILES ==========
        profiles_children = []
        
        # Liste des profils
        if check_perm('view_all_profiles', 'app_profile'):
            try:
                profiles_children.append({
                    'title': 'Liste des profils',
                    'url': reverse('app_profile:profile_list'),
                    'url_name': 'app_profile:profile_list',
                    'permission': 'view_all_profiles',
                    'resource': 'app_profile',
                })
            except NoReverseMatch:
                pass
        
        # Étudiants
        if check_perm('view_student', 'app_profile'):
            try:
                profiles_children.append({
                    'title': 'Étudiants',
                    'url': reverse('app_profile:student_list'),
                    'url_name': 'app_profile:student_list',
                    'permission': 'view_student',
                    'resource': 'app_profile',
                })
            except NoReverseMatch:
                pass
        
        # Enseignants
        if check_perm('view_teacher', 'app_profile'):
            try:
                profiles_children.append({
                    'title': 'Enseignants',
                    'url': reverse('app_profile:teacher_list'),
                    'url_name': 'app_profile:teacher_list',
                    'permission': 'view_teacher',
                    'resource': 'app_profile',
                })
            except NoReverseMatch:
                pass
        
        # Parents
        if check_perm('view_parent', 'app_profile'):
            try:
                profiles_children.append({
                    'title': 'Parents',
                    'url': reverse('app_profile:parent_list'),
                    'url_name': 'app_profile:parent_list',
                    'permission': 'view_parent',
                    'resource': 'app_profile',
                })
            except NoReverseMatch:
                pass
        
        # Mon profil (accessible à tous)
        try:
            profiles_children.append({
                'title': 'Mon profil',
                'url': reverse('app_profile:profile_view'),
                'url_name': 'app_profile:profile_view',
                'permission': None,
                'resource': None,
            })
        except NoReverseMatch:
            pass
        
        # Menu Profiles (si au moins un enfant est disponible)
        if profiles_children:
            profiles_item = {
                'title': 'Profiles',
                'icon': 'iconoir-user',
                'url': None,
                'url_name': None,
                'permission': 'view_profile',
                'resource': 'app_profile',
                'children': profiles_children,
                'is_active': request.path.startswith('/profiles/') and not request.path.startswith('/profiles/dashboard/'),
            }
            
            if should_show_menu(profiles_item):
                sidebar_menu_items.append(profiles_item)
        
        # ========== ACADEMIC ==========
        academic_children = []
        
        # Années scolaires
        if is_admin(profile) or check_perm('view_academic_year', 'app_academic'):
            try:
                academic_children.append({
                    'title': 'Années scolaires',
                    'url': reverse('app_academic:academic_year_list'),
                    'url_name': 'app_academic:academic_year_list',
                    'permission': 'view_academic_year',
                    'resource': 'app_academic',
                })
            except NoReverseMatch:
                pass
        
        # Niveaux
        if is_admin(profile) or check_perm('view_class', 'app_academic'):
            try:
                academic_children.append({
                    'title': 'Niveaux',
                    'url': reverse('app_academic:grade_list'),
                    'url_name': 'app_academic:grade_list',
                    'permission': 'view_class',
                    'resource': 'app_academic',
                })
            except NoReverseMatch:
                pass
        
        # Salles de classe
        if is_admin(profile) or check_perm('view_class', 'app_academic'):
            try:
                academic_children.append({
                    'title': 'Salles de classe',
                    'url': reverse('app_academic:classroom_list'),
                    'url_name': 'app_academic:classroom_list',
                    'permission': 'view_class',
                    'resource': 'app_academic',
                })
            except NoReverseMatch:
                pass
        
        # Classes
        if is_admin(profile) or check_perm('view_class', 'app_academic'):
            try:
                academic_children.append({
                    'title': 'Classes',
                    'url': reverse('app_academic:class_list'),
                    'url_name': 'app_academic:class_list',
                    'permission': 'view_class',
                    'resource': 'app_academic',
                })
            except NoReverseMatch:
                pass
        
        # Matières
        if is_admin(profile) or check_perm('view_subject', 'app_academic'):
            try:
                academic_children.append({
                    'title': 'Matières',
                    'url': reverse('app_academic:subject_list'),
                    'url_name': 'app_academic:subject_list',
                    'permission': 'view_subject',
                    'resource': 'app_academic',
                })
            except NoReverseMatch:
                pass
        
        # Emploi du temps
        if is_admin(profile) or check_perm('view_schedule', 'app_academic'):
            try:
                academic_children.append({
                    'title': 'Emploi du temps',
                    'url': reverse('app_academic:schedule_list'),
                    'url_name': 'app_academic:schedule_list',
                    'permission': 'view_schedule',
                    'resource': 'app_academic',
                })
            except NoReverseMatch:
                pass
        
        # Afficher le menu SEULEMENT si on a au moins un enfant disponible
        if academic_children:
            academic_item = {
                'title': 'Académique',
                'icon': 'iconoir-book',
                'url': None,
                'url_name': None,
                'permission': None,  # Pas de permission requise si on est déjà dans la condition
                'resource': 'app_academic',
                'children': academic_children,
                'is_active': request.path.startswith('/academic/'),
            }
            sidebar_menu_items.append(academic_item)
        
        # ========== GRADES ==========
        grades_children = []
        
        # Évaluations
        if is_admin(profile) or check_perm('view_assessment', 'app_grades'):
            try:
                grades_children.append({
                    'title': 'Évaluations',
                    'url': reverse('app_grades:assessment_list'),
                    'url_name': 'app_grades:assessment_list',
                    'permission': 'view_assessment',
                    'resource': 'app_grades',
                })
            except NoReverseMatch:
                pass
        
        # Notes
        if is_admin(profile) or check_perm('view_grade', 'app_grades'):
            try:
                grades_children.append({
                    'title': 'Notes',
                    'url': reverse('app_grades:grade_list'),
                    'url_name': 'app_grades:grade_list',
                    'permission': 'view_grade',
                    'resource': 'app_grades',
                })
            except NoReverseMatch:
                pass
        
        # Bulletins
        if is_admin(profile) or check_perm('view_report_card', 'app_grades'):
            try:
                grades_children.append({
                    'title': 'Bulletins',
                    'url': reverse('app_grades:report_card_list'),
                    'url_name': 'app_grades:report_card_list',
                    'permission': 'view_report_card',
                    'resource': 'app_grades',
                })
            except NoReverseMatch:
                pass
        
        # Barèmes
        if is_admin(profile) or check_perm('view_grade', 'app_grades'):
            try:
                grades_children.append({
                    'title': 'Barèmes',
                    'url': reverse('app_grades:grade_scale_list'),
                    'url_name': 'app_grades:grade_scale_list',
                    'permission': 'view_grade',
                    'resource': 'app_grades',
                })
            except NoReverseMatch:
                pass
        
        # Catégories
        if is_admin(profile) or check_perm('view_assessment', 'app_grades'):
            try:
                grades_children.append({
                    'title': 'Catégories',
                    'url': reverse('app_grades:grade_category_list'),
                    'url_name': 'app_grades:grade_category_list',
                    'permission': 'view_assessment',
                    'resource': 'app_grades',
                })
            except NoReverseMatch:
                pass
        
        # Afficher le menu SEULEMENT si on a au moins un enfant disponible
        if grades_children:
            grades_item = {
                'title': 'Notes',
                'icon': 'iconoir-document',
                'url': None,
                'url_name': None,
                'permission': None,  # Pas de permission requise si on est déjà dans la condition
                'resource': 'app_grades',
                'children': grades_children,
                'is_active': request.path.startswith('/grades/'),
            }
            sidebar_menu_items.append(grades_item)
        
        # ========== ATTENDANCE ==========
        attendance_children = []
        
        # Présences
        if is_admin(profile) or check_perm('view_attendance', 'app_attendance'):
            try:
                attendance_children.append({
                    'title': 'Présences',
                    'url': reverse('app_attendance:attendance_list'),
                    'url_name': 'app_attendance:attendance_list',
                    'permission': 'view_attendance',
                    'resource': 'app_attendance',
                })
            except NoReverseMatch:
                pass
        
        # Absences
        if is_admin(profile) or check_perm('view_absence', 'app_attendance'):
            try:
                attendance_children.append({
                    'title': 'Absences',
                    'url': reverse('app_attendance:absence_list'),
                    'url_name': 'app_attendance:absence_list',
                    'permission': 'view_absence',
                    'resource': 'app_attendance',
                })
            except NoReverseMatch:
                pass
        
        # Justificatifs
        if is_admin(profile) or check_perm('view_excuse', 'app_attendance'):
            try:
                attendance_children.append({
                    'title': 'Justificatifs',
                    'url': reverse('app_attendance:excuse_list'),
                    'url_name': 'app_attendance:excuse_list',
                    'permission': 'view_excuse',
                    'resource': 'app_attendance',
                })
            except NoReverseMatch:
                pass
        
        # Règles de présence
        if is_admin(profile) or check_perm('view_attendance', 'app_attendance'):
            try:
                attendance_children.append({
                    'title': 'Règles de présence',
                    'url': reverse('app_attendance:attendance_rule_list'),
                    'url_name': 'app_attendance:attendance_rule_list',
                    'permission': 'view_attendance',
                    'resource': 'app_attendance',
                })
            except NoReverseMatch:
                pass
        
        # Afficher le menu SEULEMENT si on a au moins un enfant disponible
        if attendance_children:
            attendance_item = {
                'title': 'Présences',
                'icon': 'iconoir-calendar',
                'url': None,
                'url_name': None,
                'permission': None,  # Pas de permission requise si on est déjà dans la condition
                'resource': 'app_attendance',
                'children': attendance_children,
                'is_active': request.path.startswith('/attendance/'),
            }
            sidebar_menu_items.append(attendance_item)
        
        # ========== CONFIGURATION (Admin uniquement) ==========
        if is_admin(profile) or check_perm('manage_permissions', 'app_config') or \
           check_perm('assign_role_permissions', 'app_config'):
            config_children = []
            
            # Gestion des rôles
            if check_perm('manage_permissions', 'app_config') or \
               check_perm('assign_role_permissions', 'app_config'):
                try:
                    config_children.append({
                        'title': 'Gestion des rôles',
                        'url': reverse('app_profile:roles_management'),
                        'url_name': 'app_profile:roles_management',
                        'permission': 'manage_permissions',
                        'resource': 'app_config',
                    })
                except NoReverseMatch:
                    pass
            
            # Vérifications (si permission)
            if check_perm('manage_verifications', 'app_profile'):
                try:
                    config_children.append({
                        'title': 'Vérifications',
                        'url': reverse('app_profile:verification_management'),
                        'url_name': 'app_profile:verification_management',
                        'permission': 'manage_verifications',
                        'resource': 'app_profile',
                    })
                except NoReverseMatch:
                    pass
            
            if config_children:
                config_item = {
                    'title': 'Configuration',
                    'icon': 'iconoir-settings',
                    'url': None,
                    'url_name': None,
                    'permission': 'manage_permissions',
                    'resource': 'app_config',
                    'children': config_children,
                    'is_active': request.path.startswith('/profiles/roles-management/') or \
                                request.path.startswith('/profiles/verifications/'),
                }
                
                sidebar_menu_items.append(config_item)
        
        context['sidebar_menu'] = sidebar_menu_items
        
    except Exception as e:
        # En cas d'erreur, retourner un menu vide
        pass
    
    return context

