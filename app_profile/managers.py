"""
Managers pour les modèles de l'application app_profile.

Ce module contient les managers personnalisés pour gérer les requêtes complexes
et la logique métier liée aux profils et organisations.
"""

from django.db import models
from django.contrib.auth.models import User

class ProfileManager(models.Manager):
    """
    Manager personnalisé pour le modèle Profile.

    Contient les méthodes de requête spécifiques aux profils utilisateurs.
    """

    def get_profiles_by_user(self, user):
        """
        Retourne le profil associé à un utilisateur spécifique.

        Args:
            user (User): Instance de l'utilisateur

        Returns:
            Profile: Profil de l'utilisateur
        """
        return self.get(user=user)

    def get_active_profiles(self):
        """
        Retourne tous les profils actifs.

        Returns:
            QuerySet: Profils actifs
        """
        return self.filter(is_active=True)

    def get_profiles_created_after(self, date):
        """
        Retourne les profils créés après une date spécifique.

        Args:
            date (datetime): Date de référence

        Returns:
            QuerySet: Profils créés après la date spécifiée
        """
        return self.filter(created_at__gt=date)

class ParentProfileManager(models.Manager):
    """
    Manager personnalisé pour le modèle ParentProfile.
    
    Contient les méthodes de requête spécifiques aux profils parents.
    """
    
    def get_active_profiles(self):
        """
        Retourne tous les profils parents actifs.
        
        Returns:
            QuerySet: Profils parents actifs
        """
        return self.filter(is_active=True)
    
    def get_profiles_by_country(self, country_code):
        """
        Retourne les profils parents d'un pays spécifique.
        
        Args:
            country_code (str): Code du pays
            
        Returns:
            QuerySet: Profils parents du pays spécifié
        """
        return self.filter(country__code=country_code)
    
    def get_profiles_with_children(self):
        """
        Retourne les profils parents qui ont des enfants.
        
        Returns:
            QuerySet: Profils parents avec enfants
        """
        return self.filter(childprofile__isnull=False).distinct()
    
    def get_profiles_with_organisations(self):
        """
        Retourne les profils parents qui possèdent des organisations.
        
        Returns:
            QuerySet: Profils parents avec organisations
        """
        return self.filter(organisation__isnull=False).distinct()

class ChildProfileManager(models.Manager):
    """
    Manager personnalisé pour le modèle ChildProfile.
    
    Contient les méthodes de requête spécifiques aux profils enfants.
    """
    
    def get_children_by_parent(self, parent_profile):
        """
        Retourne tous les enfants d'un parent spécifique.
        
        Args:
            parent_profile (ParentProfile): Profil du parent
            
        Returns:
            QuerySet: Enfants du parent spécifié
        """
        return self.filter(parent=parent_profile)
    
    def get_children_by_age_range(self, min_age=None, max_age=None):
        """
        Retourne les enfants dans une tranche d'âge spécifique.
        
        Args:
            min_age (int, optional): Âge minimum
            max_age (int, optional): Âge maximum
            
        Returns:
            QuerySet: Enfants dans la tranche d'âge
        """
        queryset = self.all()
        
        if min_age is not None:
            queryset = queryset.filter(age__gte=min_age)
        
        if max_age is not None:
            queryset = queryset.filter(age__lte=max_age)
            
        return queryset
    
    def get_children_by_relationship(self, relationship):
        """
        Retourne les enfants selon leur relation avec le parent.
        
        Args:
            relationship (str): Type de relation (son, daughter, ward, etc.)
            
        Returns:
            QuerySet: Enfants avec la relation spécifiée
        """
        return self.filter(relationship=relationship)

class OrganisationManager(models.Manager):
    """
    Manager personnalisé pour le modèle Organisation.
    
    Contient les méthodes de requête spécifiques aux organisations.
    """
    
    def get_organisations_by_owner(self, owner_profile):
        """
        Retourne toutes les organisations d'un propriétaire spécifique.
        
        Args:
            owner_profile (ParentProfile): Profil du propriétaire
            
        Returns:
            QuerySet: Organisations du propriétaire
        """
        return self.filter(owner=owner_profile)
    
    def get_organisations_with_members(self):
        """
        Retourne les organisations qui ont des membres.
        
        Returns:
            QuerySet: Organisations avec membres
        """
        return self.filter(members__isnull=False).distinct()
    
    def get_organisations_by_member_count(self, min_count=None, max_count=None):
        """
        Retourne les organisations selon le nombre de membres.
        
        Args:
            min_count (int, optional): Nombre minimum de membres
            max_count (int, optional): Nombre maximum de membres
            
        Returns:
            QuerySet: Organisations selon le nombre de membres
        """
        queryset = self.annotate(member_count=models.Count('members'))
        
        if min_count is not None:
            queryset = queryset.filter(member_count__gte=min_count)
        
        if max_count is not None:
            queryset = queryset.filter(member_count__lte=max_count)
            
        return queryset
