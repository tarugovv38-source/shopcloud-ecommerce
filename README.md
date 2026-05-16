# ShopCloud — E-Commerce com Docker

Cloud Computing · Sistemas de Informação
Tema: Infraestrutura para um Pequeno E-Commerce

---

## Descricao da Aplicacao

Sistema de gestao para um pequeno e-commerce, permitindo cadastro e consulta de produtos, clientes e pedidos via interface web.

Executado em ambiente totalmente containerizado com dois containers separados comunicando-se via rede Docker interna:

- Container app — API + interface web (Python · FastAPI · Jinja2)
- Container db — Banco de dados relacional (PostgreSQL 16)

---

## Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework web | FastAPI |
| Templates HTML | Jinja2 |
| Banco de dados | PostgreSQL 16 |
| Containerizacao | Docker + Docker Compose |
| Driver DB | psycopg2-binary |
| Servidor ASGI | Uvicorn |

---

## Arquitetura

    +-------------------------------------------------------------+
    |                  Docker Network: ecommerce-net              |
    |                                                             |
    |  +----------------------+       +------------------------+  |
    |  |   Container: app     |       |    Container: db       |  |
    |  |                      |------>|                        |  |
    |  |  Python + FastAPI    | :5432 |  PostgreSQL 16         |  |
    |  |  Jinja2 templates    |       |                        |  |
    |  |  Porta: 8000         |       |  Volume: postgres-data |  |
    |  +----------------------+       +------------------------+  |
    |           |                                                  |
    +-----------|--------------------------------------------------+
                | :8000
         +------+------+
         |  Navegador  |
         |  (usuario)  |
         +-------------+

Fluxo:
1. Usuario acessa http://localhost:8000
2. FastAPI processa a requisicao e consulta/grava no PostgreSQL
3. Jinja2 renderiza o HTML e retorna para o navegador
4. Dados persistem no volume postgres-data

Operacoes CRUD implementadas:
- Produtos: criar, listar, remover
- Clientes: criar, listar, remover
- Pedidos: criar, listar, remover

---

## Estrutura do Projeto

    projeto/
    +-- app/
    |   +-- main.py
    |   +-- requirements.txt
    |   +-- templates/
    |       +-- base.html
    |       +-- index.html
    |       +-- produtos.html
    |       +-- clientes.html
    |       +-- pedidos.html
    +-- Dockerfile
    +-- docker-compose.yml
    +-- .env.example
    +-- .gitignore
    +-- README.md
    +-- evidencias/

---

## Variaveis de Ambiente

| Variavel | Padrao | Descricao |
|---|---|---|
| DB_NAME | ecommerce | Nome do banco |
| DB_USER | postgres | Usuario do PostgreSQL |
| DB_PASSWORD | postgres | Senha do PostgreSQL |
| APP_PORT | 8000 | Porta da aplicacao |

---

## Portas Utilizadas

| Container | Porta interna | Porta externa | Servico |
|---|---|---|---|
| ecommerce-app | 8000 | 8000 | Aplicacao web |
| ecommerce-db | 5432 | interna | PostgreSQL |

---

## Como Executar

Pre-requisitos:
- Docker instalado
- Docker Compose (incluso no Docker Desktop)

1. Clone o repositorio

    git clone https://github.com/tarugovv38-source/shopcloud-ecommerce.git
    cd shopcloud-ecommerce

2. Inicie os containers

    docker compose up --build

3. Acesse a aplicacao

Abra o navegador em: http://localhost:8000

4. Parar os containers

    docker compose stop
    docker compose down
    docker compose down -v

---

## Comandos Uteis

    docker ps
    docker compose logs app
    docker volume ls
    docker exec -it ecommerce-db psql -U postgres -d ecommerce

---

## Instrucoes do Docker Compose

| Configuracao | Descricao |
|---|---|
| networks: ecommerce-net | Rede bridge isolada |
| volumes: postgres-data | Persistencia do PostgreSQL |
| depends_on + healthcheck | App aguarda banco estar pronto |
| environment | Variaveis injetadas nos containers |
| restart: unless-stopped | Reinicializacao automatica |

---

## DockerHub

    docker pull tarugovv38-source/shopcloud-ecommerce:latest

