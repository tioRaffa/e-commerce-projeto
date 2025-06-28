import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from users.models import ProfileModel


@pytest.mark.django_db
class TestUserMeEndpoint:
    url = '/api/v1/users/me/'

    def test_get_me_anauthorized(self):
        """
        Testa se o endpoint 'me' retorna o status HTTP 403 FORBIDDEN quando uma requisição GET é feita sem autenticação.
        Este teste garante que usuários não autenticados não conseguem acessar informações protegidas do usuário atual,
        assegurando a correta implementação das permissões de acesso na API.
        """
        
        client = APIClient()
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_me_success(self):
        """
        Testa o endpoint 'me' da API de usuários para garantir que um usuário autenticado
        consiga recuperar com sucesso suas próprias informações.
        Cenário:
        - Um usuário é criado com nome de usuário, email e primeiro nome.
        - Um cliente autenticado como esse usuário faz uma requisição GET para o endpoint.
        - O teste verifica se:
            - O status de resposta é 200 OK.
            - O campo 'first_name' retornado corresponde ao do usuário criado.
            - O campo 'email' retornado corresponde ao do usuário criado.
            - O campo 'cpf' do perfil do usuário é None (não definido).
        """

        user = User.objects.create_user(username='username-teste', email='email@teste.com', first_name='fname-teste')

        cliente = APIClient()
        cliente.force_authenticate(user=user)

        response = cliente.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == user.first_name
        assert response.data['email'] == user.email
        assert response.data['profile']['cpf'] is None

    def test_patch_me_success(self):
        """
        Testa a atualização parcial (PATCH) dos dados do usuário autenticado na API.
        Este teste verifica se um usuário autenticado consegue atualizar com sucesso seus próprios dados, incluindo campos do modelo User (como 'first_name') e campos relacionados ao perfil (como 'cpf'). O teste autentica um usuário fictício, envia uma requisição PATCH com os novos dados e valida se a resposta possui status HTTP 200 OK, além de confirmar que os dados foram realmente atualizados no banco de dados.
        Cenários verificados:
        - Atualização do campo 'first_name' do usuário.
        - Atualização do campo 'cpf' do perfil relacionado ao usuário.
        - Retorno do status HTTP 200 OK após a atualização.
        """
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
        """
        Testa se o endpoint PATCH do usuário autenticado ('me') impede a alteração do campo CPF.
        Este teste garante que, ao tentar atualizar o CPF do perfil do usuário autenticado via requisição PATCH,
        a API retorna o status HTTP 400 (Bad Request) e indica corretamente o erro relacionado ao campo 'cpf'.
        O objetivo é assegurar que o CPF, uma informação sensível e única, não possa ser alterado por meio da API
        após o cadastro inicial do usuário.
        Cenário:
            - Um usuário é criado com um CPF definido em seu perfil.
            - O usuário é autenticado e tenta alterar o CPF via PATCH.
            - A resposta deve ser 400 BAD REQUEST e conter referência ao campo 'cpf' no erro.
        """
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
    

    def test_put_me_method_not_allowed(self):
        """
        Testa se o método HTTP PUT não é permitido no endpoint 'me'.
        Este teste cria um usuário de teste, autentica uma requisição usando esse usuário
        e tenta enviar uma requisição PUT para o endpoint definido por `self.url` com dados de exemplo.
        O teste verifica se a resposta retorna o status HTTP 405 (Method Not Allowed), 
        garantindo que o endpoint não aceita requisições PUT, conforme esperado pela API.
        Cenário:
            - Usuário autenticado tenta atualizar informações pessoais via PUT.
            - Espera-se que a API retorne 405 Method Not Allowed.
        """
        
        user = User.objects.create_user(username='username-teste', email='email@teste.com')
        cliente = APIClient()
        cliente.force_authenticate(user=user)

        put_data = {
            "first_name": "bla"
        }
        response = cliente.put(self.url, data=put_data, format='json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_patch_me_invalid_cpf_format(self):
        """
        Testa se a API retorna erro ao tentar atualizar o CPF do usuário com um formato inválido.
        Este teste autentica um usuário, tenta atualizar o campo 'cpf' do perfil com um valor inválido (mais dígitos do que o permitido)
        e verifica se a resposta da API possui o status HTTP 400 (BAD REQUEST). Também valida se a resposta contém a chave 'cpf' 
        indicando que houve erro de validação especificamente neste campo.
        Cenário:
            - Usuário autenticado.
            - PATCH na rota de atualização do próprio perfil com CPF inválido.
            - Espera-se resposta 400 e mensagem de erro relacionada ao campo 'cpf'.
        """
        user = User.objects.create_user(username='username-teste', email='email@teste.com')

        cliente = APIClient()
        cliente.force_authenticate(user=user)
        
        patch_data = {
            "profile": {
                "cpf": '123456789101112'
            }
        }

        response = cliente.patch(self.url, data=patch_data, format='json')
        user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cpf' in response.data or 'profile' in response.data and 'cpf' in response.data['profile']