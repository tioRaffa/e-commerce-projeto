from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from firebase_admin import auth as firebase_auth
from .models import ProfileModel

User = get_user_model()

class FirebaseAuthentication(BaseAuthentication):
    def get_token_from_header(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        parts = auth_header.split()

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
    
    def _get_or_create_local_user(self, decoded_token):
        uid = decoded_token("uid")
        email = decoded_token("email", "")
        name = decoded_token("name", "")
        first_name = name.split(" ")[0] if name else ""

        user, _ =User.objects.get_or_create(
            username=uid,
            defaults={
                "email": email,
                "first_name": first_name,
            }
        )
        return user
    
    def authenticate(self, request):
        token = self.get_token_from_header(request=request)
        if not token:
            return None
        
        decoded_token = self._verify_firebase_token(token=token)
        user = self._get_or_create_local_user(decoded_token=decoded_token)
        ProfileModel.objects.get_or_create(user=user)

        return (user, None)