"""
Utilitaires pour la gestion des OTP avec Twilio.

Ce module contient les fonctions pour envoyer des SMS via Twilio
et gérer les codes OTP pour la vérification des numéros de téléphone.
"""

import os
from django.conf import settings
from app_config.models import PhoneOTP
from twilio.rest import Client


def send_otp_via_twilio(phone_number, code):
    """
    Envoie un code OTP via SMS en utilisant Twilio.
    
    Args:
        phone_number (str): Numéro de téléphone au format international (ex: 242061234567)
        code (str): Code OTP à envoyer
    
    Returns:
        tuple: (success: bool, message_sid: str or None)
    """
    try:
        # Récupérer les credentials Twilio depuis les settings
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        
        # Vérifier que les credentials sont configurés
        if not all([account_sid, auth_token]):
            print("[WARNING] Twilio non configure - Mode developpement")
            print(f"[DEV] OTP pour {phone_number}: {code}")
            return True, None  # En dev, on simule un succès
        
        # Créer le client Twilio
        client = Client(account_sid, auth_token)
        
        # Formatter le numéro avec le '+'
        formatted_phone = f"+{phone_number}" if not phone_number.startswith('+') else phone_number
        
        # Message à envoyer
        message_body = f"Votre code de verification Monity World est: {code}. Valide pendant {settings.TIME_EXPIRE_OTP} minutes."
        
        # Envoyer le SMS via Twilio
        # Si from_number est configuré, on l'utilise, sinon Twilio utilise le numéro par défaut
        message_params = {
            'body': message_body,
            'to': formatted_phone
        }
        
        if from_number:
            message_params['from_'] = from_number
        
        message = client.messages.create(**message_params)
        
        print(f"[SUCCESS] SMS envoye a {formatted_phone} - SID: {message.sid}")
        return True, message.sid
        
    except ImportError:
        print("[WARNING] Module Twilio non installe - Mode developpement")
        print(f"[DEV] OTP pour {phone_number}: {code}")
        return True, None  # En dev, on simule un succès
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Erreur lors de l'envoi du SMS: {error_msg}")
        
        # Afficher des détails supplémentaires en mode développement
        if hasattr(e, 'msg'):
            print(f"[ERROR] Message d'erreur: {e.msg}")
        if hasattr(e, 'code'):
            print(f"[ERROR] Code d'erreur: {e.code}")
        
        return False, None


def generate_and_send_otp(phone_number):
    """
    Génère un OTP et l'envoie via SMS.
    
    Args:
        phone_number (str): Numéro de téléphone normalisé
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Récupérer le code généré
        otp = PhoneOTP.generateOtp(phone_number)
        
        # Envoyer via Twilio
        sent, message_sid = send_otp_via_twilio(phone_number, otp)
        # sent, message_sid = True, "Success-SID-Placeholder"  # Placeholder for testing without Twilio

        if sent:
            if message_sid:
                return True, f"OTP sent successfully (SID: {message_sid})"
            else:
                return True, "OTP sent successfully (dev mode)"
        else:
            return False, "Failed to send OTP"
            
    except Exception as e:
        return False, f"Error generating OTP: {str(e)}"


def validate_otp(phone_number, code):
    """
    Valide un code OTP pour un numéro de téléphone.
    
    Args:
        phone_number (str): Numéro de téléphone normalisé
        code (str): Code OTP à valider
    
    Returns:
        bool: True si l'OTP est valide, False sinon
    """
    return PhoneOTP.validateOtp(phone_number, code)

