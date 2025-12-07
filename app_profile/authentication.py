"""
Système d'authentification personnalisé pour l'application app_profile.

Ce module contient une classe d'authentification basée sur les tokens JWE
(JSON Web Encryption) pour Django REST Framework.
"""

from rest_framework import authentication, exceptions
from django.contrib.auth.models import User
from Monity_World.module_monity import decode_jwe_token


class JWEAuthentication(authentication.BaseAuthentication):
    """
    Authentification personnalisée basée sur les tokens JWE.
    
    Cette classe permet d'authentifier les utilisateurs via un Bearer Token
    JWE dans le header Authorization.
    
    Format attendu du header:
        Authorization: Bearer <jwe_token>
    
    Méthodes:
        authenticate(request): Authentifie la requête avec le token JWE
    """
    
    keyword = 'Bearer'
    
    def authenticate(self, request):
        """
        Authentifie la requête en validant le token JWE.
        
        Args:
            request: Objet Request DRF
        
        Returns:
            tuple: (user, token) si authentification réussie
            None: Si pas de token fourni
        
        Raises:
            AuthenticationFailed: Si le token est invalide ou expiré
        """
        # Récupérer le header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            # Pas de header Authorization, on ne tente pas d'authentifier
            return None
        
        # Vérifier le format du header
        parts = auth_header.split()
        
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed(
                'Invalid authorization header format. Expected: Bearer <token>'
            )
        
        if parts[0].lower() != self.keyword.lower():
            # Ce n'est pas un Bearer token, on laisse d'autres authentifications essayer
            return None
        
        token = parts[1]
        
        # Décoder et valider le token JWE
        try:
            payload = decode_jwe_token(token)
            
            if not payload:
                raise exceptions.AuthenticationFailed('Invalid or expired token')
            
            # Extraire l'ID utilisateur du payload
            user_id = payload.get('user_id')
            
            if not user_id:
                raise exceptions.AuthenticationFailed('Token payload is missing user_id')
            
            # Récupérer l'utilisateur
            try:
                user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not found or inactive')
            
            # Retourner l'utilisateur et le token
            return (user, token)
            
        except exceptions.AuthenticationFailed:
            # Propager les erreurs d'authentification
            raise
        except Exception as e:
            # Erreur lors du décodage du token
            raise exceptions.AuthenticationFailed(f'Token validation failed: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Retourne la valeur du header WWW-Authenticate pour les réponses 401.
        
        Args:
            request: Objet Request DRF
        
        Returns:
            str: Valeur du header WWW-Authenticate
        """
        return f'{self.keyword} realm="api"'

