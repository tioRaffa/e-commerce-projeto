from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    model = User
    fields = [
        'id',
        'username',
        'email',
        'first_name'
    ]
