# App: Orders

O app `orders` orquestra todo o fluxo de checkout, desde o carrinho de compras até a criação do pedido, cálculo de frete, pagamento e acompanhamento. É o app mais complexo e central para a lógica de negócio do e-commerce.

---

## 📂 Estrutura de Arquivos

```
orders/
├── migrations/         # Migrações do banco de dados para os modelos de pedido
├── models/
│   ├── order_model.py    # Modelo principal `OrderModel`
│   └── order_item_model.py # Modelo para os itens dentro de um pedido
├── serializer/
│   ├── order_serializer.py # Serializers para criação e leitura de pedidos
│   └── order_item_serializer.py # Serializer para os itens do pedido
├── services/
│   ├── stripe_service.py   # Lógica de negócio para interagir com a API da Stripe
│   ├── melhor_envio.py   # Lógica para calcular frete com a API do Melhor Envio
│   └── sendgrid.py       # (Futuro) Lógica para envio de e-mails transacionais
├── views/
│   ├── cart_view.py        # API para gerenciamento do carrinho de compras (baseado em sessão)
│   ├── shipping_options.py # API para calcular as opções de frete
│   └── order_viewset.py    # ViewSet principal para criar e gerenciar pedidos
└── urls.py               # Rotas de URL específicas do app `orders`
```

---

## ✨ Funcionalidades Principais

1.  **Carrinho de Compras Persistente por Sessão:**
    *   A `CartAPIView` gerencia um carrinho de compras que não exige que o usuário esteja logado.
    *   Os itens do carrinho são armazenados na **sessão do Django**, com um tempo de expiração de 60 minutos.

2.  **Cálculo de Frete em Tempo Real:**
    *   A `ShippingOptions` view se integra com a API do **Melhor Envio** para calcular e retornar uma lista de opções de frete com base no CEP de destino e nos produtos do carrinho.

3.  **Geração de Etiquetas de Frete:**
    *   Após um pedido ser pago (status `PROCESSING`), um administrador pode acionar a geração da etiqueta de frete.
    *   O serviço `generate_shipping_label_service` se comunica com a API do Melhor Envio para:
        a. Adicionar o frete ao carrinho do Melhor Envio.
        b. "Pagar" pelo frete (em ambiente de sandbox).
        c. Gerar a etiqueta de envio.
        d. Obter o **código de rastreio** e salvar no pedido, mudando seu status para `SHIPPED`.

4.  **Orquestração de Checkout com Stripe:**
    *   A `OrderViewSet` centraliza o processo de checkout, criando o pedido no banco e uma **Intenção de Pagamento (Payment Intent)** na Stripe para processar a transação de forma segura no frontend.

5.  **Cancelamento de Pedidos:**
    *   Permite que um usuário cancele um pedido que ainda não foi enviado. O serviço correspondente também cancela a cobrança na Stripe.

---

## 📦 Modelos (models/)

### `OrderModel`

Representa um pedido feito por um usuário.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `user` | `ForeignKey` | O usuário que fez o pedido. |
| `address` | `ForeignKey` | O endereço de entrega selecionado. |
| `status` | `CharField` | O status atual do pedido (ex: `PENDING_PAYMENT`, `PROCESSING`, `SHIPPED`). |
| `total_items_price` | `DecimalField` | Soma dos preços de todos os itens no pedido. |
| `shipping_cost` | `DecimalField` | Custo do frete selecionado. |
| `shipping_method` | `CharField` | Nome do serviço de frete (ex: "SEDEX"). |
| `shipping_service_id` | `IntegerField` | ID do serviço de frete do Melhor Envio, usado para gerar a etiqueta. |
| `melhor_envio_order_id` | `CharField` | ID do pedido no sistema do Melhor Envio. |
| `tracking_code` | `CharField` | Código de rastreio (preenchido após a geração da etiqueta). |
| `stripe_payment_intent_id` | `CharField` | ID da transação na Stripe, para referência e reconciliação. |

### `OrderItemModel`

Representa um item específico dentro de um pedido.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `order` | `ForeignKey` | O pedido ao qual este item pertence. |
| `book` | `ForeignKey` | Referência ao `BookModel` (pode ser `NULL` se o livro for deletado). |
| `quantity` | `PositiveIntegerField` | Quantidade do livro comprada. |
| `book_title_snapshot` | `CharField` | **Snapshot** do título do livro no momento da compra. |
| `unit_price_snapshot` | `DecimalField` | **Snapshot** do preço unitário no momento da compra. |

*Nota sobre Snapshots:* Armazenar o título e o preço no momento da compra é crucial para a integridade histórica dos pedidos. Isso garante que, mesmo que o preço ou o nome de um livro mude no futuro, o registro do pedido permaneça correto.

---

## ⚙️ Endpoints da API (`/api/v1/...`)

### 1. **Gerenciamento do Carrinho**

*   **Endpoint:** `/api/v1/cart/`
*   **Métodos:**
    *   `GET`: Visualiza o conteúdo atual do carrinho na sessão.
    *   `POST`: Adiciona um livro ao carrinho. Requer `book_id` and `quantity`.
    *   `DELETE`: Remove um livro do carrinho. Requer `book_id`.
*   **Autenticação:** Não necessária.

### 2. **Cálculo de Frete**

*   **Endpoint:** `POST /api/v1/checkout/shipping-options/`
*   **Autenticação:** Obrigatória.
*   **Descrição:** Calcula as opções de frete para o carrinho atual com base em um endereço fornecido.
*   **Corpo da Requisição (JSON):**
    ```json
    {
        "address_id": 1
    }
    ```
*   **Resposta de Sucesso (200 OK):** Uma lista de objetos de frete do Melhor Envio.

### 3. **Seleção de Frete para o Carrinho**

*   **Endpoint:** `POST /api/v1/cart/select-shipping/`
*   **Autenticação:** Não necessária.
*   **Descrição:** Adiciona a opção de frete escolhida (incluindo seu ID) à sessão do carrinho. Esse ID é crucial para a posterior geração da etiqueta.
*   **Corpo da Requisição (JSON):**
    ```json
    {
        "shipping_option": {
            "id": 1, // ID do serviço de frete (ex: 1 para PAC, 2 para SEDEX)
            "name": "SEDEX",
            "price": 25.50
        }
    }
    ```

### 4. **Criação e Listagem de Pedidos**

*   **Endpoint:** `/api/v1/orders/`
*   **Métodos:**
    *   `GET`: Lista todos os pedidos feitos pelo usuário logado.
    *   `POST`: Cria um novo pedido a partir do carrinho da sessão.
*   **Autenticação:** Obrigatória.
*   **Corpo da Requisição (POST):**
    ```json
    {
        "address_id": 1
    }
    ```
*   **Resposta de Sucesso (POST - 201 Created):** O objeto do pedido recém-criado, incluindo o `client_secret` da Stripe para o pagamento.

### 5. **Cancelamento de Pedido**

*   **Endpoint:** `POST /api/v1/orders/{id}/cancel/`
*   **Autenticação:** Obrigatória.
*   **Descrição:** Permite que o usuário cancele um pedido com status `PROCESSING`. A ação também tentará cancelar a cobrança na Stripe.

### 6. **Gerar Etiqueta de Envio (Admin)**

*   **Endpoint:** `POST /api/v1/orders/{id}/ship/`
*   **Autenticação:** Obrigatória (Apenas para Administradores).
*   **Descrição:** Inicia o processo de geração da etiqueta de frete para um pedido com status `PROCESSING`. Após a conclusão, o pedido é atualizado para `SHIPPED` e o código de rastreio é salvo.
*   **Resposta de Sucesso (200 OK):** O objeto do pedido atualizado com o status e o código de rastreio.
