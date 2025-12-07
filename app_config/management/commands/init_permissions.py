"""
Commande de management pour initialiser les permissions et rôles de base.

Usage:
    python manage.py init_permissions
"""

from django.core.management.base import BaseCommand
from app_config.models import Permission, Role


class Command(BaseCommand):
    help = 'Initialize base permissions and roles for the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing permissions and roles',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        self.stdout.write('Initializing permissions and roles...')
        
        # Créer les permissions
        created_permissions = []
        updated_permissions = []
        
        # Définir les permissions de base
        permissions_data = [
            # ========== Profile Management (app_profile) ==========
            {'codename': 'view_profile', 'name': 'View Profile', 'resource': 'app_profile', 'action': 'view', 'description': 'Can view user profiles'},
            {'codename': 'create_profile', 'name': 'Create Profile', 'resource': 'app_profile', 'action': 'create', 'description': 'Can create user profiles'},
            {'codename': 'edit_profile', 'name': 'Edit Profile', 'resource': 'app_profile', 'action': 'edit', 'description': 'Can edit user profiles'},
            {'codename': 'delete_profile', 'name': 'Delete Profile', 'resource': 'app_profile', 'action': 'delete', 'description': 'Can delete user profiles'},
            {'codename': 'view_all_profiles', 'name': 'View All Profiles', 'resource': 'app_profile', 'action': 'view', 'description': 'Can view all user profiles in the system'},
            {'codename': 'verify_profile', 'name': 'Verify Profile', 'resource': 'app_profile', 'action': 'verify', 'description': 'Can submit documents for profile verification'},
            {'codename': 'manage_verifications', 'name': 'Manage Verifications', 'resource': 'app_profile', 'action': 'manage', 'description': 'Can review and approve/reject profile verifications'},
            {'codename': 'manage_roles', 'name': 'Manage Roles', 'resource': 'app_profile', 'action': 'manage', 'description': 'Can manage user roles and permissions'},
            
            # Student Management
            {'codename': 'view_student', 'name': 'View Student', 'resource': 'app_profile', 'action': 'view', 'description': 'Can view student profiles'},
            {'codename': 'create_student', 'name': 'Create Student', 'resource': 'app_profile', 'action': 'create', 'description': 'Can create student profiles'},
            {'codename': 'edit_student', 'name': 'Edit Student', 'resource': 'app_profile', 'action': 'edit', 'description': 'Can edit student profiles'},
            {'codename': 'delete_student', 'name': 'Delete Student', 'resource': 'app_profile', 'action': 'delete', 'description': 'Can delete student profiles'},
            
            # Teacher Management
            {'codename': 'view_teacher', 'name': 'View Teacher', 'resource': 'app_profile', 'action': 'view', 'description': 'Can view teacher profiles'},
            {'codename': 'create_teacher', 'name': 'Create Teacher', 'resource': 'app_profile', 'action': 'create', 'description': 'Can create teacher profiles'},
            {'codename': 'edit_teacher', 'name': 'Edit Teacher', 'resource': 'app_profile', 'action': 'edit', 'description': 'Can edit teacher profiles'},
            {'codename': 'delete_teacher', 'name': 'Delete Teacher', 'resource': 'app_profile', 'action': 'delete', 'description': 'Can delete teacher profiles'},
            
            # Parent Management
            {'codename': 'view_parent', 'name': 'View Parent', 'resource': 'app_profile', 'action': 'view', 'description': 'Can view parent profiles'},
            {'codename': 'create_parent', 'name': 'Create Parent', 'resource': 'app_profile', 'action': 'create', 'description': 'Can create parent profiles'},
            {'codename': 'edit_parent', 'name': 'Edit Parent', 'resource': 'app_profile', 'action': 'edit', 'description': 'Can edit parent profiles'},
            {'codename': 'delete_parent', 'name': 'Delete Parent', 'resource': 'app_profile', 'action': 'delete', 'description': 'Can delete parent profiles'},
            
            # ========== Academic Management (app_academic) ==========
            {'codename': 'view_academic_year', 'name': 'View Academic Year', 'resource': 'app_academic', 'action': 'view', 'description': 'Can view academic years'},
            {'codename': 'create_academic_year', 'name': 'Create Academic Year', 'resource': 'app_academic', 'action': 'create', 'description': 'Can create academic years'},
            {'codename': 'edit_academic_year', 'name': 'Edit Academic Year', 'resource': 'app_academic', 'action': 'edit', 'description': 'Can edit academic years'},
            {'codename': 'delete_academic_year', 'name': 'Delete Academic Year', 'resource': 'app_academic', 'action': 'delete', 'description': 'Can delete academic years'},
            
            {'codename': 'view_class', 'name': 'View Class', 'resource': 'app_academic', 'action': 'view', 'description': 'Can view classes'},
            {'codename': 'create_class', 'name': 'Create Class', 'resource': 'app_academic', 'action': 'create', 'description': 'Can create classes'},
            {'codename': 'edit_class', 'name': 'Edit Class', 'resource': 'app_academic', 'action': 'edit', 'description': 'Can edit classes'},
            {'codename': 'delete_class', 'name': 'Delete Class', 'resource': 'app_academic', 'action': 'delete', 'description': 'Can delete classes'},
            
            {'codename': 'view_subject', 'name': 'View Subject', 'resource': 'app_academic', 'action': 'view', 'description': 'Can view subjects'},
            {'codename': 'create_subject', 'name': 'Create Subject', 'resource': 'app_academic', 'action': 'create', 'description': 'Can create subjects'},
            {'codename': 'edit_subject', 'name': 'Edit Subject', 'resource': 'app_academic', 'action': 'edit', 'description': 'Can edit subjects'},
            {'codename': 'delete_subject', 'name': 'Delete Subject', 'resource': 'app_academic', 'action': 'delete', 'description': 'Can delete subjects'},
            
            {'codename': 'view_schedule', 'name': 'View Schedule', 'resource': 'app_academic', 'action': 'view', 'description': 'Can view schedules'},
            {'codename': 'create_schedule', 'name': 'Create Schedule', 'resource': 'app_academic', 'action': 'create', 'description': 'Can create schedules'},
            {'codename': 'edit_schedule', 'name': 'Edit Schedule', 'resource': 'app_academic', 'action': 'edit', 'description': 'Can edit schedules'},
            {'codename': 'delete_schedule', 'name': 'Delete Schedule', 'resource': 'app_academic', 'action': 'delete', 'description': 'Can delete schedules'},
            
            {'codename': 'manage_academic', 'name': 'Manage Academic', 'resource': 'app_academic', 'action': 'manage', 'description': 'Can manage all academic operations'},
            
            # ========== Grades Management (app_grades) ==========
            {'codename': 'view_assessment', 'name': 'View Assessment', 'resource': 'app_grades', 'action': 'view', 'description': 'Can view assessments'},
            {'codename': 'create_assessment', 'name': 'Create Assessment', 'resource': 'app_grades', 'action': 'create', 'description': 'Can create assessments'},
            {'codename': 'edit_assessment', 'name': 'Edit Assessment', 'resource': 'app_grades', 'action': 'edit', 'description': 'Can edit assessments'},
            {'codename': 'delete_assessment', 'name': 'Delete Assessment', 'resource': 'app_grades', 'action': 'delete', 'description': 'Can delete assessments'},
            
            {'codename': 'view_grade', 'name': 'View Grade', 'resource': 'app_grades', 'action': 'view', 'description': 'Can view student grades'},
            {'codename': 'create_grade', 'name': 'Create Grade', 'resource': 'app_grades', 'action': 'create', 'description': 'Can create student grades'},
            {'codename': 'edit_grade', 'name': 'Edit Grade', 'resource': 'app_grades', 'action': 'edit', 'description': 'Can edit student grades'},
            {'codename': 'delete_grade', 'name': 'Delete Grade', 'resource': 'app_grades', 'action': 'delete', 'description': 'Can delete student grades'},
            
            {'codename': 'view_report_card', 'name': 'View Report Card', 'resource': 'app_grades', 'action': 'view', 'description': 'Can view report cards'},
            {'codename': 'create_report_card', 'name': 'Create Report Card', 'resource': 'app_grades', 'action': 'create', 'description': 'Can create report cards'},
            {'codename': 'edit_report_card', 'name': 'Edit Report Card', 'resource': 'app_grades', 'action': 'edit', 'description': 'Can edit report cards'},
            {'codename': 'delete_report_card', 'name': 'Delete Report Card', 'resource': 'app_grades', 'action': 'delete', 'description': 'Can delete report cards'},
            
            {'codename': 'manage_grades', 'name': 'Manage Grades', 'resource': 'app_grades', 'action': 'manage', 'description': 'Can manage all grades and assessments'},
            
            # ========== Attendance Management (app_attendance) ==========
            {'codename': 'view_attendance', 'name': 'View Attendance', 'resource': 'app_attendance', 'action': 'view', 'description': 'Can view attendance records'},
            {'codename': 'create_attendance', 'name': 'Create Attendance', 'resource': 'app_attendance', 'action': 'create', 'description': 'Can create attendance records'},
            {'codename': 'edit_attendance', 'name': 'Edit Attendance', 'resource': 'app_attendance', 'action': 'edit', 'description': 'Can edit attendance records'},
            {'codename': 'delete_attendance', 'name': 'Delete Attendance', 'resource': 'app_attendance', 'action': 'delete', 'description': 'Can delete attendance records'},
            
            {'codename': 'view_absence', 'name': 'View Absence', 'resource': 'app_attendance', 'action': 'view', 'description': 'Can view absence records'},
            {'codename': 'create_absence', 'name': 'Create Absence', 'resource': 'app_attendance', 'action': 'create', 'description': 'Can create absence records'},
            {'codename': 'edit_absence', 'name': 'Edit Absence', 'resource': 'app_attendance', 'action': 'edit', 'description': 'Can edit absence records'},
            {'codename': 'delete_absence', 'name': 'Delete Absence', 'resource': 'app_attendance', 'action': 'delete', 'description': 'Can delete absence records'},
            
            {'codename': 'view_excuse', 'name': 'View Excuse', 'resource': 'app_attendance', 'action': 'view', 'description': 'Can view excuses'},
            {'codename': 'create_excuse', 'name': 'Create Excuse', 'resource': 'app_attendance', 'action': 'create', 'description': 'Can create excuses'},
            {'codename': 'edit_excuse', 'name': 'Edit Excuse', 'resource': 'app_attendance', 'action': 'edit', 'description': 'Can edit excuses'},
            {'codename': 'delete_excuse', 'name': 'Delete Excuse', 'resource': 'app_attendance', 'action': 'delete', 'description': 'Can delete excuses'},
            
            {'codename': 'manage_attendance', 'name': 'Manage Attendance', 'resource': 'app_attendance', 'action': 'manage', 'description': 'Can manage all attendance operations'},
            
            # ========== Configuration (app_config) ==========
            {'codename': 'view_config', 'name': 'View Configuration', 'resource': 'app_config', 'action': 'view', 'description': 'Can view configuration'},
            {'codename': 'view_all_users', 'name': 'View All Users', 'resource': 'app_config', 'action': 'view', 'description': 'Can view all users in the system'},
            {'codename': 'assign_role_permissions', 'name': 'Assign Role Permissions', 'resource': 'app_config', 'action': 'manage', 'description': 'Can assign permissions based on roles'},
            {'codename': 'manage_permissions', 'name': 'Manage Permissions', 'resource': 'app_config', 'action': 'manage', 'description': 'Can manage user permissions and roles'},
        ]
        
        # Créer les permissions
        self.stdout.write('\nCreating permissions...')
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                resource=perm_data['resource'],
                action=perm_data['action'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data.get('description', ''),
                    'is_active': True
                }
            )
            
            if created:
                created_permissions.append(permission)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created permission: {permission.name}'))
            elif force:
                # Mettre à jour si force est activé
                permission.name = perm_data['name']
                permission.action = perm_data['action']
                permission.description = perm_data.get('description', '')
                permission.is_active = True
                permission.save()
                updated_permissions.append(permission)
                self.stdout.write(self.style.WARNING(f'  ↻ Updated permission: {permission.name}'))
            else:
                self.stdout.write(f'  Permission already exists: {permission.name}')
        
        self.stdout.write(f'\nTotal permissions: {len(created_permissions)} created, {len(updated_permissions)} updated')

        # Créer les rôles de base
        roles_data = [
            {
                'codename': 'admin',
                'name': 'Administrateur',
                'role_type': 'system',
                'description': 'Accès complet à toutes les fonctionnalités et gestion des permissions',
                'permissions': [p['codename'] for p in permissions_data]  # Toutes les permissions
            },
            {
                'codename': 'student',
                'name': 'Étudiant',
                'role_type': 'system',
                'description': 'Rôle pour les étudiants avec permissions de base',
                'permissions': [
                    # Profil
                    'view_profile', 'edit_profile', 'verify_profile',
                    # Notes (lecture seule)
                    'view_assessment', 'view_grade', 'view_report_card',
                    # Présence (lecture seule)
                    'view_attendance', 'view_absence', 'view_excuse',
                    # Académique (lecture seule)
                    'view_academic_year', 'view_class', 'view_subject', 'view_schedule',
                ]
            },
            {
                'codename': 'teacher',
                'name': 'Enseignant',
                'role_type': 'system',
                'description': 'Rôle pour les enseignants avec permissions étendues',
                'permissions': [
                    # Profil
                    'view_profile', 'edit_profile', 'verify_profile',
                    # Notes (gestion complète)
                    'view_assessment', 'create_assessment', 'edit_assessment', 'delete_assessment',
                    'view_grade', 'create_grade', 'edit_grade', 'delete_grade',
                    'view_report_card', 'create_report_card', 'edit_report_card',
                    # Présence (gestion complète)
                    'view_attendance', 'create_attendance', 'edit_attendance',
                    'view_absence', 'create_absence', 'edit_absence',
                    'view_excuse', 'create_excuse', 'edit_excuse',
                    # Académique (lecture et modification limitée)
                    'view_academic_year', 'view_class', 'view_subject', 'view_schedule',
                    'edit_schedule',  # Peut modifier son propre emploi du temps
                    # Étudiants (lecture et consultation)
                    'view_student',
                ]
            },
            {
                'codename': 'parent',
                'name': 'Parent',
                'role_type': 'system',
                'description': 'Rôle pour les parents avec permissions de consultation',
                'permissions': [
                    # Profil
                    'view_profile', 'edit_profile', 'verify_profile',
                    # Notes des enfants (lecture seule)
                    'view_grade', 'view_report_card',
                    # Présence des enfants (lecture seule)
                    'view_attendance', 'view_absence', 'view_excuse',
                    # Académique (lecture seule)
                    'view_academic_year', 'view_class', 'view_subject', 'view_schedule',
                    # Enfants (lecture seule)
                    'view_student',
                ]
            },
            {
                'codename': 'academic_manager',
                'name': 'Gestionnaire Académique',
                'role_type': 'custom',
                'description': 'Gestionnaire avec permissions complètes sur la gestion académique',
                'permissions': [
                    # Profil
                    'view_profile', 'edit_profile', 'view_all_profiles',
                    # Académique (gestion complète)
                    'view_academic_year', 'create_academic_year', 'edit_academic_year', 'delete_academic_year',
                    'view_class', 'create_class', 'edit_class', 'delete_class',
                    'view_subject', 'create_subject', 'edit_subject', 'delete_subject',
                    'view_schedule', 'create_schedule', 'edit_schedule', 'delete_schedule',
                    'manage_academic',
                    # Étudiants, enseignants, parents (gestion)
                    'view_student', 'create_student', 'edit_student',
                    'view_teacher', 'create_teacher', 'edit_teacher',
                    'view_parent', 'create_parent', 'edit_parent',
                ]
            },
            {
                'codename': 'grades_manager',
                'name': 'Gestionnaire des Notes',
                'role_type': 'custom',
                'description': 'Gestionnaire avec permissions complètes sur les notes et évaluations',
                'permissions': [
                    # Profil
                    'view_profile', 'edit_profile', 'view_all_profiles',
                    # Notes (gestion complète)
                    'view_assessment', 'create_assessment', 'edit_assessment', 'delete_assessment',
                    'view_grade', 'create_grade', 'edit_grade', 'delete_grade',
                    'view_report_card', 'create_report_card', 'edit_report_card', 'delete_report_card',
                    'manage_grades',
                    # Étudiants (lecture)
                    'view_student',
                ]
            },
            {
                'codename': 'attendance_manager',
                'name': 'Gestionnaire de Présence',
                'role_type': 'custom',
                'description': 'Gestionnaire avec permissions complètes sur les présences et absences',
                'permissions': [
                    # Profil
                    'view_profile', 'edit_profile', 'view_all_profiles',
                    # Présence (gestion complète)
                    'view_attendance', 'create_attendance', 'edit_attendance', 'delete_attendance',
                    'view_absence', 'create_absence', 'edit_absence', 'delete_absence',
                    'view_excuse', 'create_excuse', 'edit_excuse', 'delete_excuse',
                    'manage_attendance',
                    # Étudiants (lecture)
                    'view_student',
                ]
            }
        ]
        
        # Créer les rôles
        created_roles = []
        updated_roles = []
        for role_data in roles_data:
            permissions_codenames = role_data.pop('permissions', [])
            role, created = Role.objects.get_or_create(
                codename=role_data['codename'],
                defaults={
                    **role_data,
                    'is_active': True
                }
            )
            
            if created:
                created_roles.append(role)
                self.stdout.write(self.style.SUCCESS(f'✓ Created role: {role.name}'))
            elif force:
                # Mettre à jour si force est activé
                role.name = role_data['name']
                role.role_type = role_data['role_type']
                role.description = role_data.get('description', '')
                role.is_active = True
                role.save()
                updated_roles.append(role)
                self.stdout.write(self.style.WARNING(f'↻ Updated role: {role.name}'))
            else:
                self.stdout.write(f'  Role already exists: {role.name}')
            
            # Assigner les permissions au rôle
            permissions = Permission.objects.filter(codename__in=permissions_codenames, is_active=True)
            role.permissions.set(permissions)
            
            if created or force:
                self.stdout.write(f'  → Assigned {permissions.count()} permissions to {role.name}')
        
        self.stdout.write(f'\nTotal roles: {len(created_roles)} created, {len(updated_roles)} updated')
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Successfully initialized permissions and roles!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\nPermissions: {Permission.objects.filter(is_active=True).count()} active')
        self.stdout.write(f'Roles: {Role.objects.filter(is_active=True).count()} active')
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Assign admin role to a user via Django admin or web interface')
        self.stdout.write('  2. Access /config/permissions/ to manage user permissions\n')
