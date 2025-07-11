from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import ProfileModel
from addresses.serializer import AddressSerializer
from common.validate_cpf import validar_cpf

User = get_user_model()
class ProfileReadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProfileModel
        fields = [
            'cpf', 
            'birth_date', 
            'phone_number',
            'email_verified' 
        ]
    
class UserReadSerializer(serializers.ModelSerializer):
    profile = ProfileReadSerializer(read_only=True)
    addresses = AddressSerializer(read_only=True, many=True)
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'profile',
            'addresses'
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileModel
        fields = [
            'cpf',
            'birth_date',
            'phone_number'
        ]

    def validate_cpf(self, value):
        cpf_limpo = ''.join(filter(str.isdigit, value or ''))

        if not validar_cpf(cpf_limpo):
            raise serializers.ValidationError("CPF inválido!")
        return value

    def validate(self, data):
        if 'cpf' in data:
            if self.instance and self.instance.cpf:
                raise serializers.ValidationError({
                    "cpf": "O CPF já foi definido e não pode ser alterado."
                })
        return data
        
class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=50)
    last_name = serializers.CharField(required=False, max_length=50)
    profile = ProfileUpdateSerializer(required=False)