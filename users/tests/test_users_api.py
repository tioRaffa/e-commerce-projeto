import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from users.models import ProfileModel


@pytest.mark.django_db
class TestUserMeEndpoint:
    url = '/api/v1/users/me/'

    def test_get_me_anauthorized(self):
        '''
        teste para garantir que um usuario não autenticado não consiga acessar o endpoint
        '''
        client = APIClient()
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_me_success(self):
        '''
        usuário autenticado consegue ver seus próprios dados.
        '''

        user = User.objects.create_user(username='username-teste', email='email@teste.com', first_name='fname-teste')

        cliente = APIClient()
        cliente.force_authenticate(user=user)

        response = cliente.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == user.first_name
        assert response.data['email'] == user.email
        assert response.data['profile']['cpf'] is None

    def test_patch_me_success(self):
        '''
        testando metodo patch e a primeira inserção do CPF no profile
        '''

        user = User.objects.create_user(username='username-teste', email='email@teste.com')
        cliente = APIClient()
        cliente.force_authenticate(user=user)

        patch_data = {
            "first_name": "rafael",
            "profile": {
                "cpf": "032.829.930-80"
            }
        }
        response = cliente.patch(self.url, data=patch_data, format='json')
        user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert user.first_name == 'rafael'
        assert user.profile.cpf == '032.829.930-80'

    def test_patch_me_cannot_change_cpf(self):
        '''
        teste para garantir que cpf depois de inserido, não pode mais ser atualizado
        '''
        user = User.objects.create_user(username='username-teste', email='email@teste.com')
        user.profile.cpf = '032.829.930-80'
        user.profile.save()

        cliente = APIClient()
        cliente.force_authenticate(user=user)

        patch_data = {
            "profile": {
                "cpf": "982.019.220-00"
            }
        }

        response = cliente.patch(self.url, data=patch_data, format='json')
        user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cpf' in response.data or 'profile' in response.data and 'cpf' in response.data['profile']
