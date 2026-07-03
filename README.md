# RifaFácil - API

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg?logo=python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.2%2B-green.svg?logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-API-red.svg)](https://www.django-rest-framework.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

> O projeto está sendo desenvolvido durante uma Residência Tecnológica vinculada ao Instituto Federal de Brasília - IFB.

## Sumário

- [Visão Geral](#visão-geral)
- [Problema que Resolve](#problema-que-resolve)
- [Objetivos Principais](#objetivos-principais)
- [Público-Alvo e Perfis de Acesso](#público-alvo-e-perfis-de-acesso)
- [Funcionalidades e Roadmap](#funcionalidades-e-roadmap)
- [Pacotes Utilizados](#pacotes-utilizados)
- [Documentação da API](#documentação-da-api)
- [Configuração do Ambiente](#configuração-do-ambiente)

## Visão Geral

A RifaFácil API é uma solução backend RESTful desenvolvida em Django REST Framework para criação, gestão e acompanhamento de rifas digitais. O sistema permite que organizadores cadastrem rifas, gerenciem informações da campanha, criem prêmios, gerem números automaticamente e disponibilizem a base para futuras etapas de venda, pagamentos e sorteio.

Nesta etapa, o foco principal está no backend. A API pode ser testada pelo Swagger e está preparada para ser consumida futuramente por uma interface frontend.

## Problema que Resolve

Rifas digitais costumam ser gerenciadas de forma manual, com controle separado de números, pagamentos, vendedores, prêmios e comprovantes. Isso aumenta o risco de duplicidade de números, perda de informações, dificuldade de auditoria e falta de transparência para organizadores e compradores.

A API resolve esse problema centralizando o fluxo principal da rifa em uma estrutura RESTful, com autenticação, controle de acesso, persistência relacional e regras de negócio aplicadas no backend.

## Objetivos Principais

- Centralizar a gestão de rifas digitais em uma API RESTful.
- Permitir cadastro, login, recuperação de senha e edição de perfil.
- Garantir controle inicial de acesso por papel de usuário.
- Permitir criação e gerenciamento de rifas por organizadores autenticados.
- Gerar automaticamente os números de cada rifa.
- Permitir cadastro de prêmios, galeria de imagens e descrição formatada.
- Preparar a base para vendedores, compras, comprovantes, sorteios e relatórios.

## Público-Alvo e Perfis de Acesso

A RifaFácil atende organizadores, vendedores, compradores e visitantes, com permissões definidas de acordo com o perfil de acesso ao sistema.

| Perfil | Tipo de acesso | Principais permissões |
|--------|----------------|-----------------------|
| Organizador | Autenticado | Criar e gerenciar rifas, editar perfil, cadastrar prêmios e acompanhar dados da rifa |
| Vendedor | Autenticado | Perfil previsto para próximas etapas, criado futuramente pelo organizador |
| Comprador | Público | Perfil previsto para fluxo público de compra em próximas sprints |
| Visitante | Público | Pode acessar endpoints públicos, como status e documentação |

## Funcionalidades e Roadmap

A evolução do projeto foi planejada em etapas incrementais, contemplando os principais módulos da solução:

- [x] Sistema de autenticação com JWT, login por e-mail e senha, recuperação de senha e edição de perfil.
- [x] Controle inicial de acesso por papéis, com cadastro público de organizador e bloqueio de cadastro público para vendedor.
- [x] CRUD de rifas para organizadores autenticados.
- [x] Geração automática dos números ao criar uma rifa.
- [x] Exclusão lógica de rifas sem vendas.
- [x] Bloqueio de alteração de valor e quantidade de números após primeira venda.
- [x] Cadastro de prêmios por rifa, com limite de até 5 prêmios.
- [x] Suporte a descrição formatada, imagem principal, galeria de imagens e link de transmissão.
- [x] Gestão de vendedores, com criação de usuário, senha gerada e comissão fixa por número.
- [x] Associação de vendedores a rifas específicas.
- [x] Dashboard inicial do vendedor, com rifas associadas, resumo e listagem de vendas preparada para o módulo de transações.
- [x] Página pública da rifa via slug, com números, prêmios, progresso e vendedores ativos.
- [x] Reserva de números com dados do comprador, CPF obrigatório e vendedor opcional.
- [ ] Upload de comprovante e expiração automática de reservas.
- [ ] Aprovação e rejeição de pagamentos.
- [ ] Sorteio, comentários moderados, relatórios e deploy.

## Pacotes Utilizados

| Pacote | Descrição |
|--------|-----------|
| django | Framework web principal |
| djangorestframework | Toolkit para construção de APIs REST |
| djangorestframework-simplejwt | Autenticação JWT |
| django-filter | Base para filtragem de consultas |
| drf-spectacular | Documentação Swagger/OpenAPI |
| django-environ | Gerenciamento de variáveis de ambiente |

> Consulte o arquivo `requirements.txt` para a lista completa de dependências do backend.

## Documentação da API

A documentação interativa completa está disponível na rota `/api/docs/` utilizando Swagger UI.

Com o servidor rodando, acesse:

```text
http://127.0.0.1:8000/api/docs/
```

### Endpoints Principais

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/api/` | Lista as principais rotas disponíveis da API | Pública |
| GET | `/api/status/` | Verifica se a API está online | Pública |
| POST | `/api/cadastro/` | Cadastro de usuário organizador | Pública |
| POST | `/api/login/` | Login com e-mail e senha | Pública |
| POST | `/api/renovar-token/` | Renovação de token JWT | Pública |
| POST | `/api/recuperar-senha/` | Solicitação de recuperação de senha | Pública |
| POST | `/api/redefinir-senha/{uid}/{token}/` | Redefinição de senha com link simulado | Pública |
| GET/PATCH | `/api/perfil/` | Consulta e edição do perfil autenticado | Requerida |
| GET/POST | `/api/rifas/` | Lista e cria rifas do organizador | Requerida |
| GET/PUT/PATCH/DELETE | `/api/rifas/{id}/` | Detalha, edita e faz exclusão lógica da rifa | Requerida |
| POST | `/api/rifas/{id}/galeria/` | Adiciona imagem à galeria da rifa | Requerida |
| GET | `/api/rifa/{slug}/public/` | Exibe dados públicos da rifa, números, prêmios, progresso e vendedores | Pública |
| POST | `/api/rifa/{id}/reservar/` | Cria reserva de números para comprador | Pública |
| GET/POST | `/api/rifas/{rifa_pk}/premios/` | Lista e cria prêmios da rifa | Requerida |
| GET/PUT/PATCH/DELETE | `/api/rifas/{rifa_pk}/premios/{id}/` | Detalha, edita e remove prêmio | Requerida |
| GET/POST | `/api/vendedores/` | Lista e cadastra vendedores do organizador | Requerida |
| GET/PUT/PATCH | `/api/vendedores/{id}/` | Detalha e edita dados do vendedor | Requerida |
| POST | `/api/vendedores/{id}/associar-rifa/` | Associa vendedor a uma rifa do organizador | Requerida |
| DELETE | `/api/vendedores/{id}/remover-rifa/` | Desativa associação entre vendedor e rifa | Requerida |
| GET | `/api/vendedor/rifas/` | Lista rifas associadas ao vendedor autenticado | Requerida |
| GET | `/api/vendedor/vendas/` | Lista vendas do vendedor autenticado | Requerida |
| GET | `/api/vendedor/resumo/` | Exibe resumo de vendas e comissão do vendedor | Requerida |

## Configuração do Ambiente

Siga os passos abaixo para configurar o ambiente local.

1. Clone o repositório:

   ```bash
   git clone https://github.com/ludy-d3v/sistema-de-rifa-ifb.git
   cd sistema-de-rifa-ifb
   ```

2. Crie e ative o ambiente virtual:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:

   ```bash
   copy .env.example .env
   ```

5. Crie o banco de dados:

   ```bash
   python manage.py migrate
   ```

6. Crie um superusuário para acessar o painel administrativo:

   ```bash
   python manage.py createsuperuser
   ```

   Para carregar dados de demonstração no ambiente local, também é possível executar:

   ```bash
   python manage.py seed_demo
   ```

7. Inicie o servidor:

   ```bash
   python manage.py runserver
   ```
