# App: Books

O app `books` é responsável por todo o gerenciamento do catálogo de livros da loja. Ele inclui os modelos de dados para livros, autores e categorias, além de funcionalidades para popular o banco de dados através da API do Google Books e expor o catálogo via API REST.

---

## 📂 Estrutura de Arquivos

```
books/
├── migrations/         # Migrações do banco de dados para os modelos de livros
├── models/
│   ├── book_model.py     # Modelo principal `BookModel`
│   ├── author_model.py   # Modelo para os autores dos livros
│   └── category_model.py # Modelo para as categorias dos livros
├── serializers/
│   └── book_serializer.py # Serializer para o modelo de livro
├── services/
│   └── google_books_api.py # Lógica de negócio para interagir com a Google Books API
├── views/
│   └── book_view.py      # `BookViewSetAPI` que expõe os endpoints do catálogo
└── management/commands/  # Comandos customizados do Django para gerenciar o catálogo
```

---

## ✨ Funcionalidades Principais

1.  **Catálogo de Livros:**
    *   O `BookModel` armazena informações detalhadas sobre cada livro, incluindo título, descrição, ISBN, dimensões, peso, preço e estoque.
    *   A API permite a listagem pública dos livros ativos (`is_active=True`), com suporte a filtros, busca textual e ordenação.

2.  **Integração com Google Books API:**
    *   O app possui uma camada de serviço (`google_books_api.py`) dedicada a se comunicar com a [Google Books API](https://developers.google.com/books).
    *   **Busca:** Permite pesquisar livros na API do Google diretamente através de um endpoint, facilitando a descoberta de novos títulos para importação.
    *   **Importação:** Um endpoint permite importar um livro específico usando seu `google_books_id`, preenchendo automaticamente a maioria dos campos do `BookModel`.

3.  **Gerenciamento via Linha de Comando:**
    *   Foram criados `management commands` customizados para facilitar a administração do catálogo sem a necessidade de uma interface gráfica.
    *   É possível pesquisar, importar um livro específico, importar por categoria ou criar múltiplos livros aleatórios para testes (veja a seção "Gerenciamento do Catálogo" no `README.md` principal).

4.  **Permissões Flexíveis:**
    *   A listagem e visualização de livros são públicas (`IsStaffAuthOrReadOnly`).
    *   A criação, atualização e exclusão de livros, bem como a importação, são restritas a usuários com permissão de `staff` (administradores).

---

## 📦 Modelos (models/)

### `BookModel`

O modelo central do app.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `google_books_id` | `CharField(20)` | ID único do livro na Google Books API. |
| `title` | `CharField(150)`| Título do livro. |
| `authors` | `ManyToManyField` | Relação com o modelo `AuthorModel`. |
| `categories` | `ManyToManyField` | Relação com o modelo `CategoryModel`. |
| `publisher` | `CharField(500)`| Editora do livro. |
| `description` | `TextField` | Descrição/sinopse do livro. |
| `isbn_13` / `isbn_10` | `CharField` | ISBNs únicos do livro. |
| `thumbnail_url` | `URLField` | URL para a imagem da capa do livro. |
| `price` | `DecimalField` | Preço de venda do livro. |
| `stock` | `PositiveIntegerField` | Quantidade disponível em estoque. |
| `is_active` | `BooleanField` | Se `True`, o livro aparece na loja para os clientes. |
| `weight_g`, `height_cm`, etc. | `DecimalField` | Dimensões e peso do livro, essenciais para o cálculo de frete. |

### `AuthorModel` e `CategoryModel`

Modelos simples que armazenam, respectivamente, os nomes dos autores e das categorias, permitindo relações `muitos-para-muitos` com o `BookModel`.

---

## ⚙️ Endpoints da API (`/api/v1/books/`)

### 1. **Listar e Buscar Livros**

*   **Endpoint:** `GET /api/v1/books/`
*   **Método:** `GET`
*   **Autenticação:** Não necessária.
*   **Descrição:** Retorna uma lista paginada de todos os livros ativos. Suporta os seguintes query params:
    *   `search`: Busca textual nos campos `title`, `isbn_13`, `isbn_10`, `authors__name` e `categories__name`.
        *   Exemplo: `/api/v1/books/?search=Duna`
    *   `ordering`: Ordena os resultados. Campos disponíveis: `price`, `created_at`, `page_count`.
        *   Exemplo: `/api/v1/books/?ordering=-price` (ordem decrescente de preço).
*   **Resposta de Sucesso (200 OK):** Uma lista paginada de objetos de livro.

<details>
  <summary>▶️ Exemplo no Insomnia</summary>

  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

### 2. **Visualizar um Livro Específico**

*   **Endpoint:** `GET /api/v1/books/{id}/`
*   **Método:** `GET`
*   **Autenticação:** Não necessária.
*   **Descrição:** Retorna os detalhes completos de um único livro ativo.

<details>
  <summary>▶️ Exemplo no Insomnia</summary>

  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

### 3. **Buscar Livros na API do Google**

*   **Endpoint:** `GET /api/v1/books/search-google/`
*   **Método:** `GET`
*   **Autenticação:** Restrito a `staff`.
*   **Descrição:** Realiza uma busca na Google Books API.
*   **Query Param Obrigatório:** `q` (termo da busca).
    *   Exemplo: `/api/v1/books/search-google/?q=Frank Herbert`
*   **Resposta de Sucesso (200 OK):** Uma lista de resultados da API do Google, contendo `title`, `authors` e `google_books_id`.

<details>
  <summary>▶️ Exemplo no Insomnia</summary>

  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>

### 4. **Importar Livro da API do Google**

*   **Endpoint:** `POST /api/v1/books/import-google/`
*   **Método:** `POST`
*   **Autenticação:** Restrito a `staff`.
*   **Descrição:** Importa um livro para o banco de dados local usando seu ID do Google.
*   **Corpo da Requisição (JSON):**

    ```json
    {
        "google_books_id": "gK98gXR8onwC"
    }
    ```

*   **Resposta de Sucesso (201 Created):** O objeto do livro recém-criado e salvo no banco de dados.
*   **Resposta de Erro (409 Conflict):** Se o livro com este `google_books_id` já existir no banco.

<details>
  <summary>▶️ Exemplo no Insomnia</summary>

  <!-- Adicione aqui o print da sua requisição no Insomnia -->
</details>
