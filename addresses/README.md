# App: Addresses

O app `addresses` é responsável pelo gerenciamento dos endereços dos usuários. Ele permite que cada usuário cadastre, visualize, atualize e remova seus próprios endereços, que serão utilizados para o cálculo de frete e entrega de pedidos.

---

## 📂 Estrutura de Arquivos

```
addresses/
├── migrations/         # Migrações do banco de dados para o modelo de endereço
├── models.py           # Define o modelo de dados `AddressModel`
├── serializer.py       # Serializer para converter o modelo de endereço em JSON e vice-versa
├── views.py            # Contém a `AddressViewset` que define a lógica dos endpoints da API
└── tests/              # Testes automatizados para a API de endereços
```

---

## ✨ Funcionalidades Principais

1.  **CRUD de Endereços:**
    *   Fornece operações completas de Criar, Ler, Atualizar e Deletar (CRUD) para os endereços.
    *   A API é projetada para ser RESTful, utilizando os métodos HTTP padrão (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).

2.  **Segurança e Isolamento de Dados:**
    *   Um usuário só pode visualizar e gerenciar seus próprios endereços. A `AddressViewset` filtra automaticamente os endereços com base no usuário autenticado (`request.user`).
    *   A permissão `IsAuthenticated` garante que apenas usuários logados possam interagir com os endpoints.

3.  **Limite de Endereços:**
    *   Para evitar abuso e manter a consistência dos dados, a lógica de negócio impõe um limite de **3 endereços por usuário**. Uma tentativa de criar um quarto endereço resultará em um erro `400 Bad Request`.

4.  **Integração com o Perfil do Usuário:**
    *   Os endereços são diretamente associados ao perfil do usuário, permitindo que outros apps, como o de `orders`, acessem facilmente o endereço de entrega selecionado durante o checkout.

---

## 📦 Modelo (models.py)

### `AddressModel`

Representa um endereço físico de um usuário.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `user` | `ForeignKey` | Chave estrangeira para o modelo `User`, estabelecendo o dono do endereço. |
| `zip_code` | `CharField(9)` | CEP do endereço. |
| `street` | `CharField(250)`| Nome da rua. |
| `number` | `CharField(20)` | Número do imóvel (pode ser alfanumérico, ex: "123A"). |
| `complement` | `CharField(250)`| Complemento do endereço (ex: "apto 33"), opcional. |
| `neighborhood`| `CharField(250)`| Bairro. |
| `city` | `CharField(150)`| Cidade. |
| `state` | `CharField(2)` | Sigla do estado (ex: "SP", "RJ"). |
| `country` | `CharField(50)` | País (padrão: "Brasil"). |
| `is_primary` | `BooleanField` | Indica se este é o endereço principal do usuário (ainda não utilizado na lógica principal). |

---

## ⚙️ Endpoints da API (`/api/v1/addresses/`)

### 1. **Listar Endereços do Usuário**

*   **Endpoint:** `GET /api/v1/addresses/`
*   **Método:** `GET`
*   **Autenticação:** Obrigatória.
*   **Descrição:** Retorna uma lista com todos os endereços cadastrados pelo usuário logado.
*   **Resposta de Sucesso (200 OK):**

    ```json
    [
        {
            "id": 1,
            "zip_code": "12345-678",
            "street": "Rua Exemplo",
            "number": "100",
            "complement": "Apto 10",
            "neighborhood": "Centro",
            "city": "Cidade Exemplo",
            "state": "EX",
            "country": "Brasil",
            "is_primary": false
        }
    ]
    ```
<details>
  <summary>▶️ Exemplo no Insomnia</summary>
   <img width="1919" height="987" alt="Image" src="https://github.com/user-attachments/assets/3c754baa-f440-4815-abf8-6b1cc870d177" />
  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

### 2. **Criar um Novo Endereço**

*   **Endpoint:** `POST /api/v1/addresses/`
*   **Método:** `POST`
*   **Autenticação:** Obrigatória.
*   **Descrição:** Cria um novo endereço para o usuário logado. Falhará se o usuário já tiver 3 endereços.
*   **Corpo da Requisição (JSON):**

    ```json
    {
        "zip_code": "98765-432",
        "street": "Avenida Principal",
        "number": "200",
        "neighborhood": "Bairro Novo",
        "city": "Outra Cidade",
        "state": "OC"
    }
    ```

*   **Resposta de Sucesso (201 Created):** O objeto do endereço recém-criado.
*   **Resposta de Erro (400 Bad Request):** Se o limite de 3 endereços for atingido.

<details>
  <summary>▶️ Exemplo no Insomnia</summary>
   <img width="1919" height="1008" alt="Image" src="https://github.com/user-attachments/assets/c1a4e8f8-d422-4d60-adfc-691c5ec9a664" />
  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

### 3. **Visualizar, Atualizar e Deletar um Endereço Específico**

*   **Endpoint:** `/api/v1/addresses/{id}/`
*   **Métodos:** `GET`, `PUT`, `PATCH`, `DELETE`
*   **Autenticação:** Obrigatória.
*   **Descrição:**
    *   `GET`: Retorna os detalhes de um endereço específico.
    *   `PUT` / `PATCH`: Atualiza os dados de um endereço existente.
    *   `DELETE`: Remove um endereço.
*   **Segurança:** A API garante que um usuário não possa acessar ou modificar um endereço que não lhe pertence, retornando `404 Not Found` se o ID do endereço não for do usuário logado.

<details>
  <summary>▶️ Exemplo no Insomnia (GET)</summary>
   <img width="1638" height="890" alt="Image" src="https://github.com/user-attachments/assets/ddd01e12-8603-4c27-95aa-3d23789b0678" />
  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

<details>
  <summary>▶️ Exemplo no Insomnia (PATCH)</summary>
   <img width="1919" height="1014" alt="Image" src="https://github.com/user-attachments/assets/d2496bc3-40a2-4182-ac9e-765ea670cab0" />
  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

<details>
  <summary>▶️ Exemplo no Insomnia (DELETE)</summary>
   <img width="1640" height="886" alt="Image" src="https://github.com/user-attachments/assets/6a84d4c5-1765-4a59-860d-06cfcf592782" />
  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

### Testes

<details>
  <summary>▶️ Informações faltando</summary>
   <img width="1631" height="893" alt="Image" src="https://github.com/user-attachments/assets/ae5b9002-e34e-4dd7-9beb-a4d459511aac" />
  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

<details>
  <summary>▶️ CEP invalido</summary>
   <img width="1633" height="896" alt="Image" src="https://github.com/user-attachments/assets/4563bf36-f28b-4cc4-809d-57e4425842d4" />
  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>
