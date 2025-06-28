import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from addresses.models import AddressModel

@pytest.mark.django_db
class TestAddressEndpoint:

    def test_create_address(self):
        """
        Testa a criação de um novo endereço via API para um usuário autenticado.
        Este teste realiza os seguintes passos:
        1. Cria um usuário de teste.
        2. Cria um endereço associado a esse usuário.
        3. Autentica o cliente da API com o usuário criado.
        4. Envia uma requisição POST para o endpoint de criação de endereços com dados válidos.
        5. Verifica se a resposta da API possui o status HTTP 201 CREATED, indicando que o endereço foi criado com sucesso.
        Garante que o endpoint de criação de endereços está funcionando corretamente para usuários autenticados.
        """
        user = User.objects.create_user(username='teste1', email='rafael@gmail.com')

        AddressModel.objects.create(user=user, zip_code='11111111', number='1', street='Ruadokrl')

        cliente = APIClient()
        cliente.force_authenticate(user=user)

        post_data = {
            "zip_code": "88502-060",
	        "street": "Antonio Goncalves de Farias",
	        "number": 44,
	        "neighborhood": "Centro",
	        "city": "Lages",
	        "state": "SC"
            }

        response = cliente.post('/api/v1/addresses/', data=post_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
    
    def test_post_addresses_anauthorized(self):
        """
        Testa se a criação de um novo endereço via POST na API de endereços retorna o status HTTP 403 (Forbidden)
        quando o usuário não está autenticado.
        Cenário:
            - Um usuário é criado no banco de dados.
            - Um endereço é associado a esse usuário.
            - Um cliente da API (não autenticado) tenta criar um novo endereço enviando dados válidos.
        Resultado esperado:
            - A resposta da API deve ter o status HTTP 403 FORBIDDEN, indicando que a autenticação é obrigatória
              para criar um endereço.
        """
        user = User.objects.create_user(username='teste1', email='rafael@gmail.com')

        AddressModel.objects.create(user=user, zip_code='11111111', number='1', street='Ruadokrl')

        cliente = APIClient()

        post_data = {
            "zip_code": "88502-060",
	        "street": "Antonio Goncalves de Farias",
	        "number": 44,
	        "neighborhood": "Centro",
	        "city": "Lages",
	        "state": "SC"
            }

        response = cliente.post('/api/v1/addresses/', data=post_data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    
    def test_list_addresses_returns_only_own_addresses(self):
        """
        Testa se a listagem de endereços retorna apenas os endereços pertencentes ao usuário autenticado.
        Este teste cria dois usuários distintos e um endereço associado ao primeiro usuário. 
        Em seguida, autentica o segundo usuário e faz uma requisição GET para o endpoint de listagem de endereços.
        O teste verifica se a resposta contém zero endereços, garantindo que um usuário não possa visualizar endereços de outros usuários.
        Cenários verificados:
        - O status da resposta deve ser 200 OK.
        - O campo 'count' da resposta deve ser 0.
        - A lista de resultados ('results') deve estar vazia.
        """
        user_a = User.objects.create_user(username='user_a', email='user_a@gmail.com')
        user_b = User.objects.create_user(username='user_b', email='user_b@gmail.com')

        AddressModel.objects.create(user=user_a, zip_code='11111111', number='1', street='Rua do User A')

        cliente = APIClient()
        cliente.force_authenticate(user=user_b)

        response = cliente.get('/api/v1/addresses/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0

    def test_cannot_edit_another_users_address(self):
        """
        Testa se um usuário não pode editar o endereço de outro usuário.
        Este teste cria dois usuários distintos (user_a e user_b) e um endereço associado ao user_a.
        Em seguida, autentica o cliente como user_b e tenta editar o endereço pertencente ao user_a.
        O teste verifica se a resposta retorna o status HTTP 404 NOT FOUND, garantindo que um usuário
        não pode modificar endereços que não lhe pertencem.
        """
        user_a = User.objects.create_user(username='user_a', email='user_a@gmail.com')
        address_a = AddressModel.objects.create(user=user_a, zip_code='11111111', number='1', street='Rua do User A')

        user_b = User.objects.create_user(username='user_b', email='user_b@gmail.com')

        cliente = APIClient()
        cliente.force_authenticate(user=user_b)

        patch_data = {
            "number": "2"
        }
        response = cliente.patch(f'/api/v1/addresses/{address_a.id}/', data=patch_data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_address_limit_of_three(self):
        """
        Testa se o limite de três endereços por usuário é respeitado ao tentar criar um novo endereço.
        Este teste cria um usuário e associa a ele três endereços, atingindo o limite permitido.
        Em seguida, tenta criar um quarto endereço via requisição POST autenticada.
        O teste verifica se a resposta retorna o status HTTP 400 (Bad Request) e se a mensagem de erro
        indica que o limite de três endereços por usuário foi atingido.
        Cenário:
        - Usuário autenticado já possui três endereços cadastrados.
        - Ao tentar cadastrar um quarto endereço, a API deve impedir a operação e retornar mensagem apropriada.
        """
        user = User.objects.create_user(username='user_a', email='user_a@gmail.com')
        for i in range(3):
            AddressModel.objects.create(user=user, zip_code=f'0000000{i}', number=f'{i}', street=f'Rua {i}')

        cliente = APIClient()
        cliente.force_authenticate(user=user)

        post_data = {
            "zip_code": "88502-060",
	        "street": "Antonio Goncalves de Farias",
	        "number": 4,
	        "neighborhood": "Centro",
	        "city": "Lages",
	        "state": "SC"
            }
        response = cliente.post('/api/v1/addresses/', data=post_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Limite de 3 endereços por Usuario atingidos!" in response.data['detail']
