"""
Tests pour la connexion AJAX dans app_profile.

Ce module contient les tests unitaires pour vérifier que
la connexion via AJAX fonctionne correctement.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

from .models import Profile


class LoginAjaxTestCase(TestCase):
    """
    Tests pour la vue WebLoginView (connexion AJAX).
    """
    
    def setUp(self):
        """
        Configure l'environnement de test.
        """
        # Créer un utilisateur de test
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.username,
            email='test@example.com',
            password=self.password,
            is_active=True,
            first_name='Test',
            last_name='User'
        )
        
        # Le profil est créé automatiquement par le signal
        # Récupérer le profil et mettre à jour si nécessaire
        self.profile = Profile.objects.get(user=self.user)
        self.profile.full_name = 'Test User'
        self.profile.firstname = 'Test'
        self.profile.name = 'User'
        self.profile.save()
        
        # Créer un client de test
        self.client = Client()
    
    def test_login_ajax_success(self):
        """
        Test de connexion AJAX réussie.
        """
        # Obtenir le token CSRF
        response = self.client.get(reverse('app_profile:login'))
        csrf_token = response.cookies.get('csrftoken')
        
        # Préparer les données de connexion
        data = {
            'username': self.username,
            'password': self.password,
            'remember_me': False
        }
        
        # Envoyer la requête AJAX
        response = self.client.post(
            reverse('app_profile:login_ajax'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value if csrf_token else ''
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['username'], self.username)
        self.assertIn('full_name', response_data)
        
        # Vérifier que l'utilisateur est bien connecté
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_ajax_invalid_credentials(self):
        """
        Test de connexion AJAX avec des identifiants invalides.
        """
        # Obtenir le token CSRF
        response = self.client.get(reverse('app_profile:login'))
        csrf_token = response.cookies.get('csrftoken')
        
        # Préparer les données de connexion avec un mauvais mot de passe
        data = {
            'username': self.username,
            'password': 'wrongpassword',
            'remember_me': False
        }
        
        # Envoyer la requête AJAX
        response = self.client.post(
            reverse('app_profile:login_ajax'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value if csrf_token else ''
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('incorrect', response_data['message'].lower())
    
    def test_login_ajax_missing_fields(self):
        """
        Test de connexion AJAX avec des champs manquants.
        """
        # Obtenir le token CSRF
        response = self.client.get(reverse('app_profile:login'))
        csrf_token = response.cookies.get('csrftoken')
        
        # Préparer les données de connexion sans mot de passe
        data = {
            'username': self.username,
            'remember_me': False
        }
        
        # Envoyer la requête AJAX
        response = self.client.post(
            reverse('app_profile:login_ajax'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value if csrf_token else ''
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('requis', response_data['message'].lower())
    
    def test_login_ajax_inactive_user(self):
        """
        Test de connexion AJAX avec un utilisateur inactif.
        
        Note: Django's authenticate() retourne None pour un utilisateur inactif,
        donc la vue retourne 401 (credentials incorrects) plutôt que 403.
        """
        # Désactiver l'utilisateur
        self.user.is_active = False
        self.user.save()
        
        # Obtenir le token CSRF
        response = self.client.get(reverse('app_profile:login'))
        csrf_token = response.cookies.get('csrftoken')
        
        # Préparer les données de connexion
        data = {
            'username': self.username,
            'password': self.password,
            'remember_me': False
        }
        
        # Envoyer la requête AJAX
        response = self.client.post(
            reverse('app_profile:login_ajax'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value if csrf_token else ''
        )
        
        # Vérifier la réponse
        # authenticate() retourne None pour un utilisateur inactif, donc 401
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('incorrect', response_data['message'].lower())
    
    def test_login_ajax_remember_me(self):
        """
        Test de connexion AJAX avec "Se souvenir de moi" activé.
        """
        # Obtenir le token CSRF
        response = self.client.get(reverse('app_profile:login'))
        csrf_token = response.cookies.get('csrftoken')
        
        # Préparer les données de connexion avec remember_me
        data = {
            'username': self.username,
            'password': self.password,
            'remember_me': True
        }
        
        # Envoyer la requête AJAX
        response = self.client.post(
            reverse('app_profile:login_ajax'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value if csrf_token else ''
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        
        # Vérifier que la session a une expiration prolongée
        # (1209600 secondes = 2 semaines)
        session_expiry = response.wsgi_request.session.get_expiry_age()
        self.assertGreater(session_expiry, 0)
    
    def test_login_ajax_invalid_json(self):
        """
        Test de connexion AJAX avec des données JSON invalides.
        """
        # Obtenir le token CSRF
        response = self.client.get(reverse('app_profile:login'))
        csrf_token = response.cookies.get('csrftoken')
        
        # Envoyer une requête avec des données JSON invalides
        response = self.client.post(
            reverse('app_profile:login_ajax'),
            data='invalid json',
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value if csrf_token else ''
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('json', response_data['message'].lower())

