"""
Template tags personnalisés pour app_config.
"""

from django import template
from app_config.permissions import is_admin, has_permission

register = template.Library()


@register.simple_tag(name='is_admin')
def check_is_admin(profile):
    """
    Template tag pour vérifier si un profil est administrateur.
    
    Usage:
        {% load app_config_tags %}
        {% is_admin user.profile as user_is_admin %}
        {% if user_is_admin %}
            ...
        {% endif %}
    """
    if not profile:
        return False
    return is_admin(profile)


@register.simple_tag(name='user_has_permission')
def check_user_permission(profile, permission_codename, resource=None):
    """
    Template tag pour vérifier si un profil a une permission spécifique.
    
    Usage:
        {% load app_config_tags %}
        {% user_has_permission user.profile 'view_profile' 'app_profile' as can_view_profile %}
        {% if can_view_profile %}
            ...
        {% endif %}
    """
    if not profile:
        return False
    return has_permission(profile, permission_codename, resource)

