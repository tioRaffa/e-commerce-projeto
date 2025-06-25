import os
import firebase_admin
from firebase_admin import credentials
from django.conf import settings



def initializer_firebase():
    if not firebase_admin._apps:
        key_path = os.path.join(settings.BASE_DIR, 'serviceAccountKey.json')

        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            print('Firebase admin SDK incializado!')
        else:
            print('Arquivo serviceAccountkey.json não encontrado')