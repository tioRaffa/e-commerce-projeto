# Bookstore API - Backend para E-commerce

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.0-green?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Django_REST-3.15-red?style=for-the-badge&logo=django&logoColor=white" alt="Django REST Framework">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Firebase-Auth-orange?style=for-the-badge&logo=firebase&logoColor=white" alt="Firebase">
</div>

API RESTful robusta para uma plataforma de e-commerce de livros, projetada com uma arquitetura moderna, escalável e orientada a serviços para simular uma operação de vendas de produtos físicos do mundo real.

---

### ⚠️ Status do Projeto: Em Desenvolvimento Ativo ⚠️

Este é um projeto de portfólio que está sendo construído ativamente. O objetivo é explorar e implementar as melhores práticas em desenvolvimento backend, integração de APIs e arquitetura de software. As funcionalidades descritas abaixo estão sendo adicionadas de forma incremental.

**Progresso Atual:** A fundação do projeto, incluindo autenticação de usuários e gerenciamento de perfis/endereços, está concluída e testada. O próximo passo é o desenvolvimento do catálogo de livros.

---

### Arquitetura e Design

O projeto foi estruturado para ser modular e de fácil manutenção, seguindo os seguintes princípios:

* **Arquitetura de Apps por Domínio:** Cada responsabilidade principal (usuários, livros, pedidos) é isolada em seu próprio app Django, promovendo baixo acoplamento e alta coesão.
* **Autenticação Delegada:** Utiliza o **Firebase Authentication** como provedor de identidade (IdP). O backend é responsável apenas por validar os tokens JWT recebidos, não por armazenar senhas, resultando em uma arquitetura mais segura e escalável.
* **Camada de Serviço:** A lógica de comunicação com cada API externa é abstraída em uma "camada de serviço", mantendo as `views` limpas e focadas na lógica de negócio.
* **Desenvolvimento Orientado a Testes:** Após a validação manual dos endpoints, uma suíte de testes automatizados com `pytest` está sendo construída para garantir a estabilidade e prevenir regressões.

---

### Funcionalidades (Planejadas e Implementadas)

-   [x] **Autenticação Segura via Firebase:** Sistema de identidade completo com suporte a login por e-mail/senha e social (Google, Facebook, GitHub), com validação de token no backend.
-   [x] **Gerenciamento de Perfil e Endereços:** CRUD completo e seguro para endereços de usuário, onde cada usuário só pode gerenciar seus próprios dados.
-   [x] **Validação de Endereços com ViaCEP:** Lógica de backend para validar e enriquecer os dados de endereço no momento da criação, garantindo a integridade dos dados para o frete.
-   [ ] **Catálogo de Livros Automatizado:** Sistema de importação de livros usando a **Google Books API** para popular o catálogo.
-   [ ] **Cálculo de Frete em Tempo Real:** Integração com a **API do Melhor Envio** para cotar fretes com base no endereço de destino e nas dimensões/peso dos produtos.
-   [ ] **Ciclo de Pagamento:** Integração com um **Gateway de Pagamento** para processar transações financeiras.
-   [ ] **Comunicação Transacional:** Envio automático de e-mails (confirmação de pedido, notificação de envio) via **SendGrid**.
-   [ ] **Sistema de Pedidos e Carrinho:** Lógica completa para criação de pedidos a partir de um carrinho de compras baseado em sessão.

---

### Principais Endpoints da API (Até o momento)

A API segue as melhores práticas REST e utiliza paginação para listagens.

| Método | Endpoint | Descrição | Autenticação |
| :--- | :--- | :--- | :--- |
| `GET` / `PATCH` | `/api/v1/users/me/` | Busca ou atualiza os dados do perfil do usuário logado. | **Obrigatória** |
| `GET` / `POST` | `/api/v1/addresses/` | Lista ou cria novos endereços para o usuário logado. | **Obrigatória** |
| `GET`/`PUT`/`PATCH`/`DELETE` | `/api/v1/addresses/{id}/` | Gerencia um endereço específico do usuário logado. | **Obrigatória** |

---

### Próximos Passos no Desenvolvimento

O foco agora se volta para a construção do núcleo transacional do e-commerce. As próximas etapas planejadas são:

-   [ ] **Implementar o Catálogo de Livros (`apps/books`):**
    -   Finalizar o `BookViewSet` e a integração com a **Google Books API**.
    -   Criar o comando de gerenciamento para importar e sincronizar livros de forma automatizada.

-   [ ] **Desenvolver o Módulo de Pedidos (`apps/orders`):**
    -   Construir a lógica e os endpoints para `Order` e `OrderItem`. Este é o coração do e-commerce, orquestrando as seguintes integrações:
    -   **Cálculo de Frete:** Integrar com a API do **Melhor Envio** para obter cotações em tempo real com base no endereço do cliente e nas dimensões/peso dos produtos.
    -   **Processamento de Pagamento:** Implementar o fluxo de checkout com o gateway de pagamento **AbacatePay**, lidando com respostas de sucesso e falha na transação.
    -   **Comunicação com o Cliente:** Utilizar a API do **SendGrid** para o envio automático de e-mails transacionais, como confirmação de pedido e notificação de envio com código de rastreio.

-   [ ] **Expandir a Cobertura de Testes com `pytest`:**
    -   Criar testes automatizados para as novas regras de negócio dos apps `books` e `orders`, garantindo a estabilidade e a qualidade do código.

-   [ ] **Conteinerizar a Aplicação com `Docker`:**
    -   Escrever o `Dockerfile` e o `docker-compose.yml` para empacotar toda a aplicação, criando um ambiente de desenvolvimento e produção padronizado e portátil.

---
