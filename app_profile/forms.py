"""
Formulaires pour l'application app_profile.

Ce module contient tous les formulaires Django pour la gestion
des profils, élèves, enseignants et parents.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Student, Teacher, Parent
from app_config.models import Country


class LoginForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé.
    """
    username = forms.CharField(
        label="Nom d'utilisateur ou Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nom d\'utilisateur ou email'
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Se souvenir de moi",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ProfileForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier un profil.
    """
    
    class Meta:
        model = Profile
        fields = [
            'full_name', 'firstname', 'name', 'birth_date', 'gender',
            'country', 'phone', 'photo', 'role'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet'
            }),
            'firstname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'country': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de téléphone'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les pays actifs
        self.fields['country'].queryset = Country.objects.filter(is_active=True)
        self.fields['country'].empty_label = "Sélectionnez un pays"


class StudentForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier un élève.
    """
    
    class Meta:
        model = Student
        fields = [
            'student_number', 'enrollment_date', 'class_level'
        ]
        widgets = {
            'student_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro d\'élève'
            }),
            'enrollment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'class_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Niveau de classe (ex: 6ème, Terminale)'
            }),
        }
    
    def clean_student_number(self):
        """
        Valide l'unicité du numéro d'élève.
        """
        student_number = self.cleaned_data.get('student_number')
        if student_number:
            # Vérifier l'unicité sauf pour l'instance actuelle
            qs = Student.objects.filter(student_number=student_number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ce numéro d'élève existe déjà.")
        return student_number


class TeacherForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier un enseignant.
    """
    
    class Meta:
        model = Teacher
        fields = [
            'teacher_number', 'hire_date', 'specialization', 'department'
        ]
        widgets = {
            'teacher_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro d\'enseignant'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Spécialisation (ex: Mathématiques, Français)'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Département'
            }),
        }
    
    def clean_teacher_number(self):
        """
        Valide l'unicité du numéro d'enseignant.
        """
        teacher_number = self.cleaned_data.get('teacher_number')
        if teacher_number:
            # Vérifier l'unicité sauf pour l'instance actuelle
            qs = Teacher.objects.filter(teacher_number=teacher_number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ce numéro d'enseignant existe déjà.")
        return teacher_number


class ParentForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier un parent.
    """
    
    class Meta:
        model = Parent
        fields = [
            'parent_number', 'relationship_type', 'occupation', 'emergency_contact'
        ]
        widgets = {
            'parent_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de parent'
            }),
            'relationship_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Profession'
            }),
            'emergency_contact': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Options pour le type de relation
        self.fields['relationship_type'].widget = forms.Select(
            choices=[
                ('', 'Sélectionnez un type'),
                ('father', 'Père'),
                ('mother', 'Mère'),
                ('guardian', 'Tuteur'),
                ('other', 'Autre'),
            ],
            attrs={'class': 'form-select'}
        )
    
    def clean_parent_number(self):
        """
        Valide l'unicité du numéro de parent.
        """
        parent_number = self.cleaned_data.get('parent_number')
        if parent_number:
            # Vérifier l'unicité sauf pour l'instance actuelle
            qs = Parent.objects.filter(parent_number=parent_number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ce numéro de parent existe déjà.")
        return parent_number


class PasswordResetRequestForm(PasswordResetForm):
    """
    Formulaire pour demander la réinitialisation du mot de passe.
    """
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre adresse email'
        })
    )


class PasswordResetConfirmForm(SetPasswordForm):
    """
    Formulaire pour confirmer la réinitialisation du mot de passe.
    """
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nouveau mot de passe'
        })
    )
    new_password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre nouveau mot de passe'
        })
    )


class ChangePasswordForm(forms.Form):
    """
    Formulaire pour changer le mot de passe.
    """
    old_password = forms.CharField(
        label="Ancien mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre ancien mot de passe'
        })
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nouveau mot de passe'
        })
    )
    new_password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre nouveau mot de passe'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        """
        Valide que l'ancien mot de passe est correct.
        """
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("L'ancien mot de passe est incorrect.")
        return old_password
    
    def clean_new_password2(self):
        """
        Valide que les deux nouveaux mots de passe correspondent.
        """
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les deux mots de passe ne correspondent pas.")
        return password2
    
    def save(self):
        """
        Change le mot de passe de l'utilisateur.
        """
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class PhotoUploadForm(forms.ModelForm):
    """
    Formulaire pour uploader une photo de profil.
    """
    
    class Meta:
        model = Profile
        fields = ['photo']
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_photo(self):
        """
        Valide la taille et le type de la photo.
        """
        photo = self.cleaned_data.get('photo')
        if photo:
            # Vérifier la taille (max 2 Mo)
            if photo.size > 2 * 1024 * 1024:
                raise ValidationError("La photo ne doit pas dépasser 2 Mo.")
            # Vérifier le type
            if not photo.content_type.startswith('image/'):
                raise ValidationError("Le fichier doit être une image.")
        return photo

