# RifaFacil - API

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg?logo=python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.2%2B-green.svg?logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-API-red.svg)](https://www.django-rest-framework.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

API RESTful para criacao e gestao de rifas digitais, desenvolvida em Django REST Framework durante uma Residencia Tecnologica vinculada ao Instituto Federal de Brasilia - IFB.

## Sumario

- [Visao Geral](#visao-geral)
- [Funcionalidades Entregues](#funcionalidades-entregues)
- [Perfis de Acesso](#perfis-de-acesso)
- [Tecnologias](#tecnologias)
- [Configuracao do Ambiente](#configuracao-do-ambiente)
- [Documentacao Swagger](#documentacao-swagger)
- [Endpoints Principais](#endpoints-principais)
- [Exemplos de Teste](#exemplos-de-teste)
- [Testes Automatizados](#testes-automatizados)
- [Proximas Etapas](#proximas-etapas)

## Visao Geral

O RifaFacil centraliza o fluxo de uma rifa digital: cadastro de organizador, login, protecao de rotas, perfil, recuperacao de senha, criacao de rifas, geracao automatica de numeros, cadastro de premios e suporte a imagens.

Nesta etapa, o foco principal esta no backend. A API ja pode ser testada pelo Swagger e esta preparada para ser consumida futuramente por um frontend em React ou outra interface.

## Funcionalidades Entregues

### Sprint 1 e 2 - Usuarios e autenticacao

- Cadastro publico de organizador.
- Bloqueio de cadastro publico para vendedor.
- Login com e-mail e senha.
- Geracao de token JWT.
- Renovacao de token.
- Consulta de perfil autenticado.
- Edicao de perfil.
- Recuperacao de senha simulada.
- Redefinicao de senha por link com `uid` e `token`.
- Permissoes iniciais por papel de usuario.

### Sprint 3 - Gestao de Rifas

- Model `Rifa` com dados principais da campanha.
- CRUD de rifas para organizador autenticado.
- Listagem de "minhas rifas".
- Detalhe da rifa.
- Edicao da rifa.
- Exclusao logica usando o campo `ativo`.
- Rifas inativas continuam aparecendo para o organizador.
- Geracao automatica dos numeros ao criar uma rifa.
- Model `NumeroRifa` com status inicial `disponivel`.
- Bloqueio de alteracao de `valor_numero` e `total_numeros` apos primeira venda.

### Sprint 4 - Premios, Descricao Formatada e Imagens

- Campo `descricao_html` para descricao formatada.
- Campo `imagem_principal`.
- Galeria de imagens com limite de ate 5 imagens.
- Campo `link_transmissao`.
- Model `Premio`.
- CRUD de premios aninhado a rifa.
- Limite de ate 5 premios por rifa.
- Imagem opcional por premio.
- Validacao de posicao do premio entre 1 e 5.

## Perfis de Acesso

| Perfil | Tipo de acesso | Principais permissoes |
|--------|----------------|-----------------------|
| Organizador | Autenticado | Criar e gerenciar rifas, editar perfil, cadastrar premios e acompanhar dados da rifa |
| Vendedor | Autenticado | Perfil previsto para proximas etapas, criado futuramente pelo organizador |
| Comprador | Publico | Perfil previsto para fluxo publico de compra em proximas sprints |
| Visitante | Publico | Pode acessar endpoints publicos, como status e documentacao |

## Tecnologias

| Pacote | Uso |
|--------|-----|
| django | Framework web principal |
| djangorestframework | Criacao da API REST |
| djangorestframework-simplejwt | Autenticacao JWT |
| django-filter | Base para filtros em consultas |
| drf-spectacular | Documentacao Swagger/OpenAPI |
| django-environ | Variaveis de ambiente |

## Configuracao do Ambiente

1. Clone o repositorio:

   ```bash
   git clone https://github.com/ludy-d3v/sistema-de-rifa-ifb.git
   cd sistema-de-rifa-ifb
   ```

2. Crie e ative o ambiente virtual:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Instale as dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variaveis de ambiente:

   ```bash
   copy .env.example .env
   ```

5. Aplique as migracoes:

   ```bash
   python manage.py migrate
   ```

6. Inicie o servidor:

   ```bash
   python manage.py runserver
   ```

## Documentacao Swagger

Com o servidor rodando, acesse:

```text
http://127.0.0.1:8000/api/docs/
```

Status da API:

```text
http://127.0.0.1:8000/api/status/
```

## Endpoints Principais

| Metodo | Endpoint | Descricao | Autenticacao |
|--------|----------|-----------|--------------|
| GET | `/api/` | Lista rotas principais | Publica |
| GET | `/api/status/` | Verifica se a API esta online | Publica |
| GET | `/api/docs/` | Documentacao Swagger | Publica |
| POST | `/api/cadastro/` | Cadastro de organizador | Publica |
| POST | `/api/login/` | Login com e-mail e senha | Publica |
| POST | `/api/renovar-token/` | Renovacao de token JWT | Publica |
| GET | `/api/perfil/` | Consulta perfil autenticado | Requerida |
| PATCH | `/api/perfil/` | Edita perfil autenticado | Requerida |
| POST | `/api/recuperar-senha/` | Solicita recuperacao de senha simulada | Publica |
| POST | `/api/redefinir-senha/{uid}/{token}/` | Redefine senha com link simulado | Publica |
| GET | `/api/rifas/` | Lista rifas do organizador | Requerida |
| POST | `/api/rifas/` | Cria rifa e gera numeros automaticamente | Requerida |
| GET | `/api/rifas/{id}/` | Detalha uma rifa | Requerida |
| PUT/PATCH | `/api/rifas/{id}/` | Edita uma rifa | Requerida |
| DELETE | `/api/rifas/{id}/` | Faz exclusao logica da rifa | Requerida |
| POST | `/api/rifas/{id}/galeria/` | Adiciona imagem na galeria | Requerida |
| GET | `/api/rifas/{rifa_pk}/premios/` | Lista premios da rifa | Requerida |
| POST | `/api/rifas/{rifa_pk}/premios/` | Cria premio para a rifa | Requerida |
| GET | `/api/rifas/{rifa_pk}/premios/{id}/` | Detalha premio | Requerida |
| PUT/PATCH | `/api/rifas/{rifa_pk}/premios/{id}/` | Edita premio | Requerida |
| DELETE | `/api/rifas/{rifa_pk}/premios/{id}/` | Remove premio | Requerida |

## Exemplos de Teste

### 1. Cadastrar organizador

`POST /api/cadastro/`

```json
{
  "nome": "Cliente Teste",
  "email": "cliente@example.com",
  "telefone": "61999999999",
  "cpf": "",
  "papel": "organizador",
  "senha": "senha-forte-123"
}
```

### 2. Fazer login

`POST /api/login/`

```json
{
  "email": "cliente@example.com",
  "password": "senha-forte-123"
}
```

Copie o token `access` retornado e autorize no Swagger usando:

```text
Bearer SEU_TOKEN_ACCESS_AQUI
```

### 3. Consultar perfil

`GET /api/perfil/`

### 4. Editar perfil

`PATCH /api/perfil/`

```json
{
  "telefone": "61988888888",
  "cpf": "12345678900"
}
```

### 5. Recuperar senha

`POST /api/recuperar-senha/`

```json
{
  "email": "cliente@example.com"
}
```

A API retorna um `link_simulado`. Use esse link para redefinir a senha.

### 6. Redefinir senha

`POST /api/redefinir-senha/{uid}/{token}/`

```json
{
  "nova_senha": "nova-senha-123"
}
```

### 7. Criar rifa

`POST /api/rifas/`

```json
{
  "titulo": "Rifa Beneficente IFB",
  "descricao": "Rifa para arrecadacao de fundos.",
  "descricao_html": "<p><strong>Rifa beneficente</strong> com premios especiais.</p>",
  "valor_numero": "10.00",
  "total_numeros": 100,
  "data_sorteio": "2026-07-30T20:00:00-03:00",
  "chave_pix": "organizador@teste.com",
  "tempo_reserva": 30,
  "status": "rascunho",
  "link_transmissao": "https://youtube.com/live/teste"
}
```

Ao criar a rifa, a API gera automaticamente os numeros de `1` ate `total_numeros`, todos com status `disponivel`.

### 8. Listar rifas

`GET /api/rifas/`

### 9. Editar rifa

`PATCH /api/rifas/{id}/`

```json
{
  "titulo": "Rifa Beneficente IFB - Atualizada",
  "status": "ativa"
}
```

### 10. Cadastrar premios

`POST /api/rifas/{rifa_pk}/premios/`

```json
{
  "posicao": 1,
  "descricao": "Primeiro premio: Smartphone"
}
```

```json
{
  "posicao": 2,
  "descricao": "Segundo premio: Fone Bluetooth"
}
```

```json
{
  "posicao": 3,
  "descricao": "Terceiro premio: Vale compras"
}
```

### 11. Listar premios

`GET /api/rifas/{rifa_pk}/premios/`

### 12. Exclusao logica da rifa

`DELETE /api/rifas/{id}/`

Depois, liste novamente:

`GET /api/rifas/`

A rifa continua aparecendo para o organizador, mas com:

```json
{
  "ativo": false
}
```

## Testes Automatizados

Para executar os testes:

```bash
python manage.py test
```

Os testes cobrem:

- Cadastro e login.
- Perfil autenticado.
- Recuperacao e redefinicao de senha.
- Criacao de rifa.
- Geracao automatica de numeros.
- Listagem de rifas.
- Exclusao logica.
- Bloqueio de campos apos venda.
- Cadastro de premios.

## Proximas Etapas

- Criar fluxo publico de compra.
- Implementar reserva de numeros por comprador.
- Implementar expiracao automatica de reservas.
- Criar upload de comprovante de pagamento.
- Implementar aprovacao de pagamento.
- Criar modulo de vendedores.
- Criar relatorios e exportacoes.
- Desenvolver frontend para consumo da API.
