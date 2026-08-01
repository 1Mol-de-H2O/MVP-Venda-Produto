# Venda de Produtos — API Backend

API REST para uma loja geek (jogos, mangás e afins), desenvolvida em Django REST Framework. Permite que clientes comprem produtos e que vendedores cadastrem produtos, cupons e acompanhem suas vendas.

---

## Sumário

- [Como rodar o projeto](#como-rodar-o-projeto)
  - [Árvore de arquivos](#árvore-de-arquivos)
- [Autenticação](#autenticação)
- [Regras de negócio importantes](#regras-de-negócio-importantes)
- [Endpoints](#endpoints)
  - [Usuários](#usuários)
  - [Produtos](#produtos)
  - [Carrinho](#carrinho)
  - [Pedidos](#pedidos)
  - [Cupons](#cupons)
  - [Vendas do Vendedor](#vendas-do-vendedor)

---

## Como rodar o projeto

### Requisitos
- Python 3.10+
- MySQL (servidor rodando localmente ou remoto)

### Setup

```bash
# clonar o repositório e entrar na pasta do backend
git clone <url-do-repositorio>
cd backend

# criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# instalar dependências
pip install django djangorestframework mysqlclient django-cors-headers djangorestframework-simplejwt django-filter python-decouple

```
é preciso criar o arquivo .env na raiz do backend (mesma pasta do manage.py).  
Sendo o Conteúdo do `.env`:
```
SECRET_KEY=sua_secret_key_aqui
DB_NAME=venda_produtos
DB_USER=root
DB_PASSWORD=sua_senha_mysql
DB_HOST=localhost
DB_PORT=3306
```

```bash
# criar o banco no MySQL
# CREATE DATABASE venda_produtos;

# aplicar as migrations
python manage.py migrate

# criar um super usuário (opcional, mas sendo muito útil para o /admin/)
python manage.py createsuperuser

# rodar o servidor
python manage.py runserver
```

A API fica disponível em `http://127.0.0.1:8000/api/`.  
No entanto olhe a resposta do ```runserver```


### Árvore de arquivos

```
backend/
├── core/           # configurações do projeto (settings, urls)
├── usuarios/       # autenticação, cliente/vendedor
├── produtos/       # produtos e categorias
├── carrinho/       # carrinho de compras
├── pedidos/        # checkout, frete, vendas
└── cupons/         # cupons de desconto
```

---

## Autenticação

A API usa **JWT (JSON Web Token)**. Para acessar rotas protegidas, primeiro é preciso ter uma conta e obter um token.

### 1. Criar conta

```http
POST /api/usuarios/registrar/
Content-Type: application/json
```
```json
{
  "username": "badeni",
  "email": "badeni@email.com",
  "password": "senha12345",
  "cep": "35930-000"
}
```

Resposta (`201`):
```json
{
  "detail": "Usuário criado com sucesso.",
  "username": "badeni"
}
```

Toda conta nasce como **cliente**. Para vender produtos, é preciso ativar o modo vendedor (veja [tornar-se vendedor](#tornar-se-vendedor)).

### 2. Obter token

```http
POST /api/token/
Content-Type: application/json
```
```json
{
  "username": "badeni",
  "password": "senha12345"
}
```

Resposta (`200`):
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "access": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 3. Usar o token

Em toda requisição para uma rota protegida, envie o `access` token no header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

O `access` token expira em pouco tempo.

---

## Regras de negócio importantes

- **Cliente e vendedor não são contas separadas.** Toda conta começa como cliente e pode virar vendedor a qualquer momento, sem perder o histórico.
- **Frete grátis** para compras a partir de **R$ 150,00** de subtotal. Abaixo disso, o frete é calculado com base no peso total dos itens (`R$ 10,00` de taxa base + `R$ 2,50` por kg).
- **Cupons de desconto** têm código único, tipo (desconto sobre produto ou sobre frete), percentual de desconto, período de validade, valor mínimo de compra opcional e limite de usos opcional.
- **Estoque é validado antes de finalizar um pedido.** Se qualquer item do carrinho não tiver estoque suficiente, o pedido inteiro é recusado — nenhum item é descontado.
- **Preço e título do produto são congelados no pedido.** Se o vendedor alterar o preço de um produto depois, pedidos já feitos não são afetados.
- **Cada pedido pertence a um único cliente**, e cada cliente só enxerga os próprios pedidos e o próprio carrinho.

---

## Endpoints

### Usuários

#### Registrar conta
```
POST /api/usuarios/registrar/
```
**Acesso:** público  
**Body:**
```json
{
  "username": "badeni",
  "email": "badeni@email.com",
  "password": "senha12345",
  "cep": "40028-922"
}
```
`password` precisa ter no mínimo 8 caracteres. `email` e `cep` são opcionais.

#### Meu perfil
```
GET /api/usuarios/me/
```
**Acesso:** autenticado  
**Resposta:**
```json
{
  "id": 1,
  "username": "badeni",
  "email": "badeni@email.com",
  "is_vendedor": false,
  "cep": "40028-922"
}
```

#### Tornar-se vendedor
```
PATCH /api/usuarios/tornar-vendedor/
```
**Acesso:** autenticado
Ativa o modo vendedor na conta atual, sem criar uma conta nova.  

**Resposta:** 
```json
{
  "id": 1,
  "username": "badeni",
  "email": "badeni@email.com",
  "is_vendedor": true,
  "cep": "40028-922"
}
```

---

### Produtos

#### Listar / buscar produtos
```
GET /api/produtos/
GET /api/produtos/?search=naruto
```
**Acesso:** público
Busca pelo `titulo` do produto ou pelo nome da categoria.

#### Detalhe do produto
```http
GET /api/produtos/{id}/
```
**Acesso:** público

#### Criar produto
```http
POST /api/produtos/
```
**Acesso:** apenas vendedores  
**Body:**
```json
{
  "titulo": "Orbe Sobre Os Movimentos da Terra Vol. 1",
  "marca": "Panini",
  "preco": "29.90",
  "estoque": 10,
  "descricao": "Primeiro volume do mangá",
  "peso_kg": 0.3,
  "categoria": [1]
}
```
`categoria` é uma lista de IDs de categorias já existentes. O campo `vendedor` é preenchido automaticamente com o usuário autenticado.

#### Editar / remover produto
```http
PUT /api/produtos/{id}/
PATCH /api/produtos/{id}/
DELETE /api/produtos/{id}/
```
**Acesso:** apenas o vendedor dono do produto

#### Categorias
```http
GET /api/categorias/
POST /api/categorias/
```
**Acesso:** leitura pública, criação apenas por vendedores
**Body (POST):**
```json
{ 
  "nome": "Mangás" 
}
```

---

### Carrinho

Cada cliente tem um único carrinho, criado automaticamente na primeira interação.

#### Ver carrinho
```http
GET /api/carrinho/
```
**Acesso:** autenticado
**Resposta:**
```json
{
  "id": 1,
  "itens": [
    {
      "id": 3,
      "produto": 2,
      "produto_titulo": "Orbe Sobre Os Movimentos da Terra Vol. 1",
      "produto_preco": "29.90",
      "quantidade": 2,
      "subtotal": 59.8
    }
  ],
  "total": 59.8
}
```

#### Adicionar item
```http
POST /api/carrinho/adicionar/
```
**Acesso:** autenticado  
**Body:**
```json
{
  "produto": 2,
  "quantidade": 2
}
```
Se o produto já estiver no carrinho, a quantidade é somada à existente, em vez de criar uma nova linha.

#### Remover item
```http
DELETE /api/carrinho/remover/{item_id}/
```
**Acesso:** autenticado (apenas o dono do carrinho)
`item_id` é o ID do item do carrinho (não o ID do produto).

---

### Pedidos

#### Calcular frete do carrinho atual
```http
GET /api/pedidos/frete/
```
**Acesso:** autenticado  
**Resposta:**
```json
{
  "peso_total_kg": 0.6,
  "subtotal": 59.8,
  "frete": 11.5
}
```

#### Finalizar pedido (checkout)
```http
POST /api/pedidos/finalizar/
```
**Acesso:** autenticado  
**Body:**
```json
{
  "endereco_cep": "35930-000",
  "endereco_rua": "Rua São João",
  "endereco_numero": "456",
  "endereco_complemento": "Apto 789",
  "endereco_bairro": "Centro",
  "endereco_cidade": "Coronel Fabriciano",
  "endereco_estado": "MG",
  "metodo_pagamento": "cartao",
  "cupom_codigo": "PROMO10"
}
```
`endereco_complemento` e `cupom_codigo` são opcionais. `metodo_pagamento` aceita `cartao`, `boleto` ou `pix`.

**Resposta (`201`):**
```json
{
  "id": 5,
  "status": "pendente",
  "subtotal": "59.80",
  "desconto": "5.98",
  "frete": "11.50",
  "total": "65.32",
  "cupom_codigo": "PROMO10",
  "endereco_cep": "35930-000",
  "endereco_rua": "Rua São João",
  "endereco_numero": "456",
  "endereco_complemento": "Apto 789",
  "endereco_bairro": "Centro",
  "endereco_cidade": "Coronel Fabriciano",
  "endereco_estado": "MG",
  "metodo_pagamento": "cartao",
  "criado_em": "2026-07-29T10:30:45-03:00",
  "itens": [
    {
      "id": 5,
      "produto": 2,
      "titulo_produto": "Orbe Sobre Os Movimentos da Terra Vol. 1",
      "preco_unitario": "29.90",
      "quantidade": 2,
      "subtotal": 59.8
    }
  ]
}
```

O checkout verifica o estoque de todos os itens antes de confirmar, desconta o estoque, congela o preço e título de cada produto no pedido, aplica o cupom (se informado) e esvazia o carrinho.

#### Meus pedidos
```http
GET /api/pedidos/meus/
```
**Acesso:** autenticado — retorna apenas os pedidos do usuário logado

#### Detalhe do pedido
```http
GET /api/pedidos/{id}/
```
**Acesso:** autenticado (apenas o dono do pedido — outros usuários recebem `404`)

---

### Cupons

#### Criar cupom
```http
POST /api/cupons/
```
**Acesso:** apenas vendedores

**Body:**
```json
{
  "codigo": "PROMO10",
  "tipo": "produto",
  "desconto_percentual": "10.00",
  "data_inicio": "2026-07-01T00:00:00-03:00",
  "data_fim": "2026-12-31T23:59:59-03:00",
  "valor_minimo": "50.00",
  "limite_usos": 100
}
```
`tipo` aceita `produto` (desconto sobre o valor dos produtos) ou `frete`. `valor_minimo` e `limite_usos` são opcionais. O campo `vendedor` é preenchido automaticamente.

#### Listar / detalhar cupons
```http
GET /api/cupons/
GET /api/cupons/{id}/
```
**Acesso:** leitura pública

#### Validar cupom
```http
POST /api/cupons/validar/
```
**Acesso:** autenticado  
**Body:**
```json
{
  "codigo": "PROMO10",
  "valor_compra": 100
}
```
**Resposta (cupom válido):**
```json
{
  "valido": true,
  "mensagem": "Cupom válido",
  "cupom": {
    "codigo": "PROMO10",
    "tipo": "produto",
    "desconto": 10.0,
    "valor_final": 90.0
  }
}
```
`valor_compra` é opcional — se omitido, a rota só confirma se o cupom está ativo e dentro da validade, sem calcular desconto.

**Resposta (cupom inválido, `400`):**
```json
{ "detail": "Cupom fora do período de validade" }
```

---

### Vendas do Vendedor

#### Minhas vendas
```http
GET /api/pedidos/minhas-vendas/
GET /api/pedidos/minhas-vendas/?status=pago
```
**Acesso:** apenas vendedores — lista os itens vendidos de produtos do vendedor autenticado  
**Resposta:**
```json
[
  {
    "pedido_id": 5,
    "username": "badeni",
    "email": "badeni@email.com",
    "produto": "Orbe Sobre Os Movimentos da Terra Vol. 1",
    "quantidade": 2,
    "preco_unitario": 29.9,
    "subtotal": 59.8,
    "status_pedido": "pendente",
    "data": "2026-07-29T10:30:45-03:00"
  }
]
```
O parâmetro `status` é opcional e filtra por status do pedido (`pendente`, `pago`, `enviado`, `entregue`, `cancelado`).

#### Atualizar status do pedido
```http
PATCH /api/pedidos/{id}/status/
```
**Acesso:** apenas o vendedor que tem produtos naquele pedido  
**Body:**
```json
{ "status": "enviado" }
```
Valores aceitos: `pendente`, `pago`, `enviado`, `entregue`, `cancelado`.

---

## Testando

Recomenda-se usar o [Insomnia](https://insomnia.rest/download) (o qual foi usado) ou [Postman](https://www.postman.com/downloads/) para testar a API. Fluxo básico de teste:

1. Registrar um usuário (`/api/usuarios/registrar/`)
2. Obter o token (`/api/token/`)
3. Tornar-se vendedor e cadastrar uma categoria e um produto
4. Registrar um segundo usuário (cliente) para testar o fluxo de compra
5. Adicionar produtos ao carrinho e finalizar o pedido