# RifaFacil API

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg?logo=python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0%2B-green.svg?logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-API-red.svg)](https://www.django-rest-framework.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Instituicoes de Fomento e Parceria

[![Website IFB](https://img.shields.io/badge/Website-IFB-%23508C3C.svg?labelColor=%23C8102E)](https://www.ifb.edu.br/)
[![Website ihwbr](https://img.shields.io/badge/Website-ihwbr-%23DAA520.svg?labelColor=%232E2E2E)](https://hardware.org.br/)

## Sumario

- [Visao Geral](#visao-geral)
- [Problema que Resolve](#problema-que-resolve)
- [Objetivos Principais](#objetivos-principais)
- [Publico-Alvo](#publico-alvo)
- [Funcionalidades de Alto Nivel](#funcionalidades-de-alto-nivel)
- [Pacotes Utilizados](#pacotes-utilizados)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Documentacao da API](#documentacao-da-api)
- [Configuracao do Ambiente](#configuracao-do-ambiente)
- [Roadmap de Sprints](#roadmap-de-sprints)
- [Deploy](#deploy)

## Visao Geral

A RifaFacil API e uma solucao backend RESTful desenvolvida em Django para criacao, gestao e acompanhamento de rifas digitais. O sistema permite que organizadores cadastrem rifas, gerenciem vendedores, acompanhem vendas, aprovem pagamentos, realizem sorteios e disponibilizem uma pagina publica para compradores selecionarem numeros e enviarem comprovantes.

## Problema que Resolve

Rifas digitais costumam ser gerenciadas de forma manual, com controle separado de numeros, pagamentos, vendedores e comprovantes. Isso aumenta o risco de duplicidade de numeros, perda de informacoes, dificuldade de auditoria e falta de transparencia para compradores e organizadores.

A API resolve esse problema centralizando o fluxo da rifa: cadastro, reserva de numeros, controle de status, associacao de vendedores, aprovacao de pagamentos, sorteio e relatorios.

## Objetivos Principais

- Centralizar a gestao de rifas digitais em uma API RESTful.
- Permitir cadastro e autenticacao de organizadores e vendedores.
- Garantir controle de acesso por papel de usuario.
- Registrar numeros reservados, pendentes e pagos com integridade.
- Apoiar o acompanhamento financeiro e de desempenho por vendedor.
- Preparar a base do sistema para expansao com pagina publica, carrinho, comprovantes, comentarios, sorteio e relatorios.

## Publico-Alvo

- Organizadores de rifas digitais.
- Vendedores associados a campanhas de rifa.
- Compradores que acessam paginas publicas de rifas.
- Equipes academicas ou de residencia tecnologica que precisam acompanhar a evolucao do projeto por sprints.

## Funcionalidades de Alto Nivel

- Autenticacao com JWT para organizadores e vendedores.
- Cadastro, login, recuperacao de senha e edicao de perfil.
- Controle de acesso baseado em papeis.
- Gestao de rifas com status, valor por numero, quantidade total e data do sorteio.
- Cadastro de vendedores e associacao com rifas.
- Pagina publica da rifa com grade de numeros.
- Carrinho para selecao individual de numeros.
- Upload de comprovantes e aprovacao/rejeicao de pagamentos.
- Sorteio manual ou automatico com multiplos premios.
- Comentarios moderados.
- Relatorios financeiros, de compradores e de vendedores.

## Pacotes Utilizados

| Pacote | Versao | Descricao |
|--------|--------|-----------|
| django | >=5.0 | Framework web principal |
| djangorestframework | latest | Toolkit para construcao de APIs REST |
| djangorestframework-simplejwt | latest | Autenticacao JWT |
| django-filter | latest | Filtragem de consultas |
| drf-spectacular | latest | Documentacao interativa da API |
| django-environ | latest | Gerenciamento de variaveis de ambiente |
| pillow | latest | Suporte a upload e processamento basico de imagens |

> **Nota:** Consulte o arquivo `requirements.txt` para a lista completa quando o ambiente do backend estiver configurado.

## Estrutura do Projeto

```text
Sistema de Rifa Online/
├── docs/
│   └── database_diagram.png
├── manage.py
├── requirements.txt
├── rifafacil/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── raffles/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
└── README.md
```

## Documentacao da API

A documentacao interativa devera ficar disponivel em `/api/docs/` no ambiente de desenvolvimento.

### Endpoints Iniciais Planejados

| Metodo | Endpoint | Descricao | Autenticacao |
|--------|----------|-----------|--------------|
| POST | `/api/auth/register/` | Cadastro de usuario organizador ou vendedor | Publica |
| POST | `/api/auth/login/` | Login com e-mail e senha | Publica |
| POST | `/api/auth/refresh/` | Renovacao de token JWT | Publica |
| POST | `/api/auth/password-reset/` | Solicitacao de recuperacao de senha | Publica |
| GET | `/api/auth/profile/` | Consulta do perfil autenticado | Requerida |
| PATCH | `/api/auth/profile/` | Edicao de dados do perfil | Requerida |
| GET | `/api/health/` | Rota de teste da API | Publica |

## Configuracao do Ambiente

Siga os passos abaixo para configurar o ambiente local.

1. **Clone o repositorio:**

   ```bash
   git clone <https://github.com/ludy-d3v/sistema-de-rifa-ifb.git>
   cd sistema-de-rifa-online
   ```

2. **Crie um ambiente virtual:**

   ```bash
   python -m venv .venv
   ```

3. **Ative o ambiente virtual:**

   ```bash
   .venv\Scripts\activate
   ```

4. **Instale as dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure as variaveis de ambiente:**

   ```bash
   copy .env.example .env
   ```

6. **Aplique as migracoes e inicie o servidor:**

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Roadmap de Sprints

| Sprint | Foco Principal | Entregas |
|--------|----------------|----------|
| 1 | Repositorio e fundacao | README, estrutura inicial, backend rodando e rota de teste |
| 2 | Autenticacao e papeis | Cadastro, login JWT, recuperacao simulada, perfil e rotas protegidas |
| 3-4 | Gestao de rifas e premios | CRUD de rifas, multiplos premios, upload e editor de texto |
| 5-6 | Gestao de vendedores | Cadastro de vendedores, associacao a rifas e dashboard do vendedor |
| 7-8 | Pagina publica e reservas | Grade de numeros, carrinho, formulario do comprador e CPF obrigatorio |
| 9-10 | Comprovantes e pagamentos | Upload, expiracao de reservas, aprovacao e rejeicao |
| 11-12 | Sorteio, comentarios e finalizacao | Sorteio, comentarios moderados, relatorios e deploy |

## Deploy

O deploy sera definido nas proximas sprints. A previsao inicial e publicar a API em uma plataforma como Render, Railway ou Fly.io, usando PostgreSQL em producao e variaveis de ambiente para configuracoes sensiveis.
