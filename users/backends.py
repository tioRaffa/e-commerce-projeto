from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from firebase_admin import auth as firebase_auth
from .models import ProfileModel

User = get_user_model()

class FirebaseAuthentication(BaseAuthentication):
    def get_token_from_header(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        parts = auth_header.slipt()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1]

    def _verify_firebase_token(self, token):
        try:
            decode = firebase_auth.verify_id_token(token)
        except firebase_auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed("Token expirado")
        except firebase_auth.RevokedIdTokenError:
            raise exceptions.AuthenticationFailed('Token Revogado')
        except Exception:
            raise exceptions.AuthenticationFailed('Token invalido')
        
        if not decode or "uid" not in decode:
            raise exceptions.AuthenticationFailed('Token malformado ou sem UID.')
        
        return decode