# App: Users

O app `users` é o coração do sistema de gerenciamento de identidades da aplicação. Ele é responsável por gerenciar os dados do usuário, seu perfil e a autenticação, delegando a complexidade da validação de credenciais para o Firebase.

---

## 📂 Estrutura de Arquivos

```
users/
├── migrations/         # Migrações do banco de dados para os modelos de usuário
├── models/
│   ├── base.py           # Modelo base com campos comuns (created_at, updated_at)
│   └── profile.py        # Modelo de perfil do usuário (CPF, data de nascimento, etc.)
├── serializer/
│   └── user_serializer.py # Serializers para leitura e atualização de dados do usuário
├── services/
│   ├── backends.py       # Backend de autenticação customizado para validar tokens do Firebase
│   └── firebase.py       # Serviço para interagir com a API do Firebase Admin
└── views/
    └── user_viewset.py   # ViewSet que expõe os endpoints da API para o usuário
```

---

## ✨ Funcionalidades Principais

1.  **Autenticação via Firebase JWT:**
    *   O sistema não armazena senhas. Em vez disso, ele recebe um token JWT (JSON Web Token) gerado pelo **Firebase Authentication** no cabeçalho `Authorization` de cada requisição.
    *   Um `Authentication Backend` customizado (`backends.py`) intercepta esse token, utiliza o **Firebase Admin SDK** para verificá-lo e, se válido, busca ou cria o usuário correspondente no banco de dados local.
    *   Este design desacopla a gestão de identidade do backend, tornando o sistema mais seguro e permitindo a fácil integração com provedores de login social (Google, Facebook, etc.) configurados no Firebase.

2.  **Gerenciamento de Perfil do Usuário:**
    *   Além do modelo `User` padrão do Django, há um `ProfileModel` associado (`OneToOneField`) que armazena informações adicionais, como `CPF`, `data de nascimento` e `número de telefone`.
    *   A API permite que o usuário logado visualize e atualize seus próprios dados de perfil.

3.  **Segurança e Permissões:**
    *   Os endpoints são protegidos para garantir que um usuário só possa acessar e modificar seus próprios dados.
    *   Ações críticas como a alteração de CPF são restritas para evitar modificações indevidas após o primeiro registro.

---

## 📦 Modelos (models.py)

### `ProfileModel`

Armazena dados complementares do usuário.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `user` | `OneToOneField` | Chave estrangeira para o modelo `User` do Django. |
| `cpf` | `CharField(14)` | CPF do usuário (único). A validação ocorre no serializer. |
| `birth_date` | `DateField` | Data de nascimento. |
| `phone_number` | `PhoneNumberField` | Número de telefone, com validação de formato. |
| `email_verified`| `BooleanField` | Indica se o e-mail do usuário foi verificado pelo Firebase. |

---

## ⚙️ Endpoints da API (`/api/v1/users/`)

A interação com o usuário é centralizada em um único endpoint, que se comporta de maneira diferente dependendo do método HTTP.

### 1. **Visualizar e Atualizar Perfil do Usuário Logado**

*   **Endpoint:** `GET /api/v1/users/me/`
*   **Método:** `GET`
*   **Autenticação:** Obrigatória (Token Firebase JWT).
*   **Descrição:** Retorna os dados completos do usuário logado, incluindo seu perfil e endereços cadastrados.
*   **Resposta de Sucesso (200 OK):**

    ```json
    {
        "id": 1,
        "email": "user@example.com",
        "first_name": "Nome",
        "last_name": "Sobrenome",
        "profile": {
            "cpf": "123.456.789-00",
            "birth_date": "2000-01-01",
            "phone_number": "+5511999999999",
            "email_verified": true
        },
        "addresses": []
    }
    ```

---

*   **Endpoint:** `PATCH /api/v1/users/me/`
*   **Método:** `PATCH`
*   **Autenticação:** Obrigatória.
*   **Descrição:** Permite a atualização parcial dos dados do usuário e do seu perfil. O CPF, uma vez definido, não pode ser alterado.
*   **Corpo da Requisição (JSON):**

    ```json
    {
        "first_name": "Novo Nome",
        "profile": {
            "phone_number": "+5521888888888"
        }
    }
    ```

*   **Resposta de Sucesso (200 OK):** O objeto do usuário com os dados atualizados.

### Restrições

*   Os métodos `POST`, `PUT`, `DELETE` e `LIST` no endpoint `/api/v1/users/` são desabilitados (`405 Method Not Allowed`) para usuários comuns, pois a criação de usuários é gerenciada pelo Firebase, e a listagem de todos os usuários é uma ação restrita a administradores (se implementada).
