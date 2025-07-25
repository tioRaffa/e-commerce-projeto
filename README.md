
# Bookstore API - Backend para E-commerce de Livros

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.0-green?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Firebase-Auth-orange?style=for-the-badge&logo=firebase&logoColor=white" alt="Firebase Auth">
  <img src="https://img.shields.io/badge/Stripe-Payments-6772e5?style=for-the-badge&logo=stripe&logoColor=white" alt="Stripe">
  <img src="https://img.shields.io/badge/Pytest-Testing-blueviolet?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest">
  <img src="https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready">
</div>

## 📖 Visão Geral

API RESTful robusta para uma plataforma de e-commerce de livros, projetada com uma arquitetura moderna, escalável e orientada a serviços. O objetivo é simular uma operação de vendas de produtos físicos do mundo real, integrando serviços externos para autenticação, pagamento, cálculo de frete e envio de e-mails.

---

### ⚠️ Status do Projeto: Em Fases Finais ⚠️

Este projeto de portfólio está em suas fases finais de desenvolvimento. A funcionalidade principal do backend está completa, testada e conteinerizada com Docker. O pipeline de CI/CD com GitHub Actions está operacional, garantindo a automação dos testes. Os próximos passos estão focados na conclusão de integrações secundárias e na preparação para o deploy em um ambiente de produção.

---

## ✨ Arquitetura e Design

O projeto foi estruturado para ser modular, seguro e de fácil manutenção, seguindo os seguintes princípios:

*   **Arquitetura de Apps por Domínio:** Cada responsabilidade principal (usuários, livros, pedidos, carrinho) é isolada em seu próprio app Django, promovendo baixo acoplamento e alta coesão.
*   **Autenticação Delegada:** Utiliza o **Firebase Authentication** como Provedor de Identidade (IdP). O backend é responsável apenas por validar os tokens JWT recebidos, não por armazenar senhas, resultando em uma arquitetura mais segura e escalável que suporta nativamente logins sociais.
*   **Camada de Serviço (Service Layer):** A lógica de negócio complexa e a comunicação com cada API externa (Stripe, Melhor Envio, etc.) são abstraídas em uma camada de serviço (`services.py`), mantendo as `Views` limpas e focadas em orquestração.
*   **Desenvolvimento Orientado a Testes:** A aplicação possui uma suíte de testes automatizados com `pytest` que valida as regras de negócio, a segurança dos endpoints e a lógica de integração.

---

## 🚀 Funcionalidades

-   [x] **Autenticação Segura via Firebase:** Sistema de identidade completo com suporte a login por e-mail/senha e social (Google, Facebook, GitHub).
-   [x] **Gerenciamento de Perfil e Endereços:** CRUD completo e seguro, garantindo que cada usuário só possa gerenciar seus próprios dados e com um limite de até 3 endereços.
-   [x] **Validação de Endereços:** Integração com a API do **ViaCEP** no backend para validar e enriquecer dados de endereço.
-   [x] **Catálogo de Livros Automatizado:** Sistema de importação de livros usando a **Google Books API**.
-   [x] **Sistema de Carrinho de Compras:** Gestão de um carrinho temporário utilizando o framework de **sessão do Django**.
-   [x] **Ciclo de Pagamento Completo:** Integração com a **API do Stripe** (em modo de teste) para processamento seguro de pagamentos.
-   [x] **Testes Automatizados:** Suíte de testes robusta com `pytest` e `coverage` para garantir a qualidade do código.
-   [x] **Cálculo de Frete em Tempo Real:** Integração com a **API do Melhor Envio** para obter cotações de frete.
-   [x] **Conteinerização com Docker:** A aplicação e seu banco de dados são gerenciados com `Docker` e `Docker Compose` para um ambiente de desenvolvimento e produção consistente.
-   [x] **Integração Contínua (CI):** Workflow com **GitHub Actions** que roda os testes automaticamente a cada `push` ou `pull request` na branch `main`.
-   [ ] **Comunicação Transacional:** Envio automático de e-mails de confirmação e status via **SendGrid** (próximo passo).

---

## 🐳 Executando com Docker

Para rodar a aplicação localmente, você precisa ter o [Docker](https://www.docker.com/get-started) e o [Docker Compose](https://docs.docker.com/compose/install/) instalados.

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  **Configure as Variáveis de Ambiente:**
    *   Renomeie o arquivo `.env-exemple` para `.env`.
    *   Preencha todas as variáveis de ambiente necessárias no arquivo `.env`. Elas incluem as chaves de API para Stripe, Firebase, Melhor Envio e as configurações do banco de dados.

3.  **Suba os Contêineres:**
    *   Execute o comando a seguir na raiz do projeto. Ele irá construir a imagem da aplicação (se ainda não existir) e iniciar os contêineres do Django e do PostgreSQL.
    ```bash
    docker-compose up --build
    ```

4.  **Execute as Migrações (Primeira Vez):**
    *   Em um novo terminal, com os contêineres em execução, execute o comando `migrate` dentro do contêiner da aplicação web para criar as tabelas no banco de dados:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Acesse a Aplicação:**
    *   A API estará disponível em `http://localhost:8000/api/v1/`.

---

## 🔄 CI/CD com GitHub Actions

O projeto utiliza GitHub Actions para automação de testes. O workflow, definido em `.github/workflows/django_ci.yaml`, é acionado a cada `push` ou `pull request` para a branch `main`.

**O que o workflow faz:**

1.  **Configura o Ambiente:** Prepara um ambiente Ubuntu com Python 3.11 e um serviço de banco de dados PostgreSQL.
2.  **Instala Dependências:** Instala todas as dependências listadas no `requirements.txt`.
3.  **Roda os Testes:** Executa a suíte de testes com `pytest`, utilizando as `secrets` do repositório para configurar as variáveis de ambiente necessárias.

Isso garante que novas alterações não quebrem as funcionalidades existentes antes de serem mescladas à branch principal.

---

## 🛠️ Estrutura da API (Principais Endpoints)

| Método | Endpoint | Descrição | Autenticação |
| :--- | :--- | :--- | :--- |
| `GET`/`PATCH` | `/api/v1/users/me/` | Busca ou atualiza os dados do perfil do usuário logado. | **Obrigatória** |
| `GET`/`POST`/`DELETE` | `/api/v1/addresses/` | Gerencia os endereços do usuário (limite de 3). | **Obrigatória** |
| `GET`/`PUT`/`PATCH`/`DELETE`| `/api/v1/addresses/{id}/` | Gerencia um endereço específico do usuário logado. | **Obrigatória**|
| `GET`/`POST`/`DELETE` | `/api/v1/cart/` | Visualiza, adiciona ou remove itens do carrinho na sessão. | Não Necessária |
| `GET` | `/api/v1/books/` | Lista pública e paginada dos livros disponíveis, com filtros e ordenação. | Não Necessária |
| `POST` | `/api/v1/checkout/shipping-options/` | Endpoint de serviço para calcular as opções de frete. | **Obrigatória** |
| `POST` | `/api/v1/orders/` | Endpoint principal de checkout para criar um novo pedido. | **Obrigatória** |
| `POST` | `/api/v1/orders/{id}/cancel/` | Endpoint para o usuário cancelar um pedido em processamento. | **Obrigatória** |

---

### ⚙️ Gerenciamento do Catálogo via Terminal (Management Commands)

Para facilitar a população e o gerenciamento do catálogo de livros, foram criados comandos customizados do Django. Eles devem ser executados no terminal, na pasta raiz do projeto, com o ambiente virtual ativado.

#### 1\. Pesquisar Livros no Google (`search_books`)

Este comando busca livros na Google Books API para encontrar IDs que podem ser usados para importação.

  * **Comando:**
    ```bash
    python manage.py search_books "TERMO_DA_PESQUISA"
    ```
  * **Descrição:** Ele retorna uma lista de resultados com `título`, `autores` e, mais importante, o `google_books_id` de cada livro. Use-o para encontrar o ID de um livro que você deseja importar.

#### 2\. Importar um Livro Específico (`import_book`)

Uma vez que você tem um ID, este comando importa o livro para o seu banco de dados.

  * **Comando:**
    ```bash
    python manage.py import_book "GOOGLE_BOOKS_ID"
    ```
  * **Descrição:** Utiliza um `google_books_id` para importar todos os detalhes de um livro específico da API do Google e salvá-lo no banco de dados local.

#### 3\. Importar Livros por Categoria (`import_books_by_category`)

Útil para popular rapidamente o banco de dados com livros de um gênero específico.

  * **Comando:**
    ```bash
    python manage.py import_books_by_category "NOME_DA_CATEGORIA"
    ```
  * **Descrição:** Pesquisa por uma categoria na Google Books API e importa automaticamente um número pré-definido (ex: 5) dos livros mais relevantes encontrados.

#### 4\. Importação em Massa ou por Título (`create_random_books`)

Um comando versátil para gerar dados de teste ou encontrar um livro específico pelo título.

  * **Comando (por contagem):**

    ```bash
    python manage.py create_random_books --count 10
    ```

      * **Descrição:** Importa um número especificado (`10`, no exemplo) de livros de um conjunto de categorias pré-definidas. Ótimo para gerar dados de teste rapidamente.

  * **Comando (por título):**

    ```bash
    python manage.py create_random_books --title "O Senhor dos Anéis"
    ```

      * **Descrição:** Pesquisa por um título específico e importa o livro correspondente.

-----

#### Fluxo de Trabalho Recomendado

O fluxo mais comum para adicionar um livro específico ao catálogo seria:

1.  **Encontrar o ID:**

    ```bash
    python manage.py search_books "Duna Frank Herbert"
    ```

2.  **Copiar o `google_books_id`** da lista de resultados (ex: `gK98gXR8onwC`).

3.  **Importar o livro:**

    ```bash
    python manage.py import_book "gK98gXR8onwC"
    ```

4.  **Definir Preço e Estoque:** Acesse o **Django Admin** para editar o livro recém-importado, adicionando o `preço`, o `estoque` e as informações de `dimensões/peso` para o cálculo de frete.

---

## 📦 Próximos Passos

-   [ ] **Finalizar a Integração com SendGrid:** Implementar o envio de e-mails transacionais (confirmação de pedido, etc.).
-   [ ] **Deploy na Nuvem:** Publicar a aplicação em uma plataforma como [Render.com](http://Render.com) ou Heroku.
