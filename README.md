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

-   [ ] Implementar o `BookViewSet` e a integração com a Google Books API.
-   [ ] Desenvolver a lógica e os endpoints para `Orders` e `OrderItems`.
-   [ ] Conteinerizar a aplicação com **Docker** e **Docker Compose** para um ambiente de desenvolvimento e produção padronizado.
-   [ ] Escrever uma suíte de testes completa com `pytest` para garantir a cobertura das regras de negócio.

---

### Contato

* **[Seu Nome Completo]**
* **LinkedIn:** https://blogg.sorentio.no/sosiale-medier/linkedin-ekspert-dette-ma-du-gjore-med-profilen-din/7659/
* **Email:** seu.email@provedor.com