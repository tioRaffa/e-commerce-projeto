# Bookstore API - Backend para E-commerce

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.0-green?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Firebase-Auth-orange?style=for-the-badge&logo=firebase&logoColor=white" alt="Firebase Auth">
  <img src="https://img.shields.io/badge/Stripe-Payments-6772e5?style=for-the-badge&logo=stripe&logoColor=white" alt="Stripe">
  <img src="https://img.shields.io/badge/Pytest-Testing-blueviolet?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest">
  <img src="https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready">
</div>

API RESTful robusta para uma plataforma de e-commerce de livros, projetada com uma arquitetura moderna, escalável e orientada a serviços para simular uma operação de vendas de produtos físicos do mundo real.

---

### ⚠️ Status do Projeto: Em Desenvolvimento Ativo ⚠️

Este é um projeto de portfólio que está sendo construído ativamente. O objetivo é explorar e implementar as melhores práticas em desenvolvimento backend, integração de APIs e arquitetura de software. As funcionalidades descritas abaixo estão sendo adicionadas de forma incremental.

**Progresso Atual:** A fundação da aplicação (autenticação, usuários, endereços, catálogo) e o núcleo do fluxo de pagamento com Stripe estão **concluídos e testados**. A integração com os serviços de logística está sendo finalizada e a de comunicação transacional é o próximo passo.

---

### Arquitetura e Design

O projeto foi estruturado para ser modular, seguro e de fácil manutenção, seguindo os seguintes princípios:

* **Arquitetura de Apps por Domínio:** Cada responsabilidade principal (usuários, livros, pedidos, carrinho) é isolada em seu próprio app Django, promovendo baixo acoplamento e alta coesão.
* **Autenticação Delegada:** Utiliza o **Firebase Authentication** como Provedor de Identidade (IdP). O backend é responsável apenas por validar os tokens JWT recebidos, não por armazenar senhas, resultando em uma arquitetura mais segura e escalável que suporta nativamente logins sociais.
* **Camada de Serviço (Service Layer):** A lógica de negócio complexa e a comunicação com cada API externa (Stripe, Melhor Envio, etc.) são abstraídas em uma camada de serviço (`services.py`), mantendo as `Views` limpas e focadas em orquestração.
* **Desenvolvimento Orientado a Testes:** A aplicação possui uma suíte de testes automatizados com `pytest` que valida as regras de negócio, a segurança dos endpoints e a lógica de integração.

---

### Funcionalidades

-   [x] **Autenticação Segura via Firebase:** Sistema de identidade completo com suporte a login por e-mail/senha e social (Google, Facebook, GitHub).
-   [x] **Gerenciamento de Perfil e Endereços:** CRUD completo e seguro, garantindo que cada usuário só possa gerenciar seus próprios dados e com um limite de até 3 endereços.
-   [x] **Validação de Endereços:** Integração com a API do **ViaCEP** no backend para validar e enriquecer dados de endereço.
-   [x] **Catálogo de Livros Automatizado:** Sistema de importação de livros usando a **Google Books API**.
-   [x] **Sistema de Carrinho de Compras:** Gestão de um carrinho temporário utilizando o framework de **sessão do Django**.
-   [x] **Ciclo de Pagamento Completo:** Integração com a **API do Stripe** (em modo de teste) para processamento seguro de pagamentos.
-   [x] **Testes Automatizados (Base):** Suíte de testes com `pytest` para a fundação da aplicação (usuários e endereços).
-   [🚧] **Cálculo de Frete em Tempo Real:** Integração com a **API do Melhor Envio** para obter cotações de frete (em andamento).
-   [ ] **Comunicação Transacional:** Envio automático de e-mails de confirmação e status via **SendGrid**.
-   [ ] **Gestão Completa de Pedidos:** Finalização da `ViewSet` e dos serviços que orquestram todo o fluxo de checkout.

---

### Estrutura da API (Principais Endpoints)

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

### Próximos Passos no Desenvolvimento

-   [ ] **Conteinerizar a Aplicação:** Empacotar a aplicação e seus serviços com **Docker** e **Docker Compose**.
-   [ ] **Implementar CI/CD:** Criar um workflow com **GitHub Actions** para rodar testes e construir a imagem Docker automaticamente.
-   [ ] **Deploy na Nuvem:** Publicar a aplicação em uma plataforma como **Render.com**.

---