# RifaFácil - API

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg?logo=python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0%2B-green.svg?logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-API-red.svg)](https://www.django-rest-framework.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

> O projeto esta sendo desenvolvido durante uma Residência Tecnológica vinculada ao Instituto Federal de Brasilia — IFB

## Sumário

- [Visão Geral](#visão-geral)
- [Problema que Resolve](#problema-que-resolve)
- [Objetivos Principais](#objetivos-principais)
- [Publico-Alvo e Perfis de Acesso](#público-alvo-e-perfis-de-acesso)
- [Funcionalidades e Roadmap](#funcionalidades-e-roadmap)
- [Pacotes Utilizados](#pacotes-utilizados)
- [Documentação da API](#documentação-da-api)
- [Configuração do Ambiente](#configuração-do-ambiente)

## Visão Geral

A RifaFácil API é uma solução backend RESTful desenvolvida em Django para criação, gestão e acompanhamento de rifas digitais. O sistema permite que organizadores cadastrem rifas, gerenciem vendedores, acompanhem vendas, aprovem pagamentos, realizem sorteios e disponibilizem uma pagina pública para compradores selecionarem numeros e enviarem comprovantes.

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

## Público-Alvo e Perfis de Acesso

A RifaFacil atende organizadores, vendedores, compradores e visitantes, com permissoes definidas de acordo com o perfil de acesso ao sistema.

| Perfil | Tipo de acesso | Principais permissoes |
|--------|----------------|-----------------------|
| Organizador | Autenticado | Criar e gerenciar rifas, cadastrar vendedores, aprovar pagamentos, acompanhar relatorios e realizar sorteios |
| Vendedor | Autenticado | Consultar rifas associadas, acompanhar vendas realizadas e visualizar comissoes estimadas |
| Comprador | Publico | Acessar a pagina publica da rifa, escolher numeros, preencher dados e enviar comprovante |
| Visitante | Publico | Visualizar rifas publicas e acompanhar informacoes da campanha |

## Funcionalidades e Roadmap

A evolução do projeto foi planejada em etapas incrementais, contemplando os principais módulos da solução:

- [ ] Modelagem do banco de dados (Usuários, Rifas, Números, Prêmios, Vendedores, Transações, Pagamentos, Comentários e Resultados de Sorteio).
- [ ] Sistema de autenticação com JWT, login por e-mail e senha, recuperação de senha e edição de perfil.
- [ ] Autorização por níveis de acesso (Organizador, Vendedor, Comprador e Visitante), com regras de permissão por papel.
- [ ] Desenvolvimento dos endpoints REST para CRUD de rifas, prêmios, vendedores, associações, transações, pagamentos e comentários.
- [ ] Implementação das regras de negócio críticas: números únicos por rifa, reserva exclusiva, expiração seletiva e bloqueio de campos após primeira venda.
- [ ] Fluxo público de compra com seleção individual de números, carrinho, CPF obrigatório, escolha de vendedor e upload de comprovante.
- [ ] Rotinas automatizadas para expiração de reservas, sorteio na data configurada e notificações por e-mail.
- [ ] Relatórios e exportações para acompanhamento de compradores, desempenho por vendedor, valores pendentes, arrecadação e comissões.

## Pacotes Utilizados

| Pacote | Descrição |
|--------|-----------|
| django | Framework web principal |
| djangorestframework | Toolkit para construcao de APIs REST |
| djangorestframework-simplejwt | Autenticacao JWT |
| django-filter | Filtragem de consultas |
| drf-spectacular | Documentacao interativa da API |
| django-environ | Gerenciamento de variaveis de ambiente |
| pillow | Suporte a upload e processamento basico de imagens |

> **Nota:** Consulte o arquivo `requirements.txt` para a lista completa quando o ambiente do backend estiver configurado.

## Documentação da API

A documentação interativa completa (com Schemas e testes em tempo real) está disponível na rota `/api/docs/` utilizando o Swagger UI.

### Endpoints Iniciais Planejados

| Metodo | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/api/cadastro/` | Cadastro de usuario organizador | Publica |
| POST | `/api/login/` | Login com e-mail e senha | Publica |
| POST | `/api/renovar-token/` | Renovacao de token JWT | Publica |
| POST | `/api/recuperar-senha/` | Solicitacao de recuperacao de senha | Publica |
| GET | `/api/perfil/` | Consulta do perfil autenticado | Requerida |
| PATCH | `/api/perfil/` | Edicao de dados do perfil | Requerida |
| GET | `/api/status/` | Rota de teste da API | Publica |

> Os vendedores serao cadastrados pelos organizadores e receberão suas credenciais de acesso por e-mail.

## Configuração do Ambiente

Siga os passos abaixo para configurar o ambiente local.

1. **Clone o repositorio:**

   ```bash
   git clone https://github.com/ludy-d3v/sistema-de-rifa-ifb.git
   cd Sistema-de-rifa-Online
   ```

2. **Crie um ambiente virtual:**

   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual:**

   ```bash
   .\venv\Scripts\activate
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
