# ShopCloud — E-Commerce com Docker

> Trabalho 02 · Cloud Computing · Sistemas de Informação  
> Tema: **Infraestrutura para um Pequeno E-Commerce** 🛒

---

## Descrição da Aplicação

Sistema de gestão para um pequeno e-commerce, permitindo cadastro e consulta de **produtos**, **clientes** e **pedidos** via interface web.

Executado em ambiente totalmente containerizado com dois containers separados comunicando-se via rede Docker interna:

- **Container `app`** — API + interface web (Python · FastAPI · Jinja2)
- **Container `db`** — Banco de dados relacional (PostgreSQL 16)

---

## Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework web | FastAPI |
| Templates HTML | Jinja2 |
| Banco de dados | PostgreSQL 16 |
| Containerização | Docker + Docker Compose |
| Driver DB | psycopg2-binary |
| Servidor ASGI | Uvicorn |

---

## Arquitetura
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network: ecommerce-net             │
│                                                             │
│  ┌─────────────────────┐       ┌──────────────────────────┐ │
│  │   Container: app    │       │    Container: db          │ │
│  │                     │──────▶│                          │ │
│  │  Python + FastAPI   │ :5432 │  PostgreSQL 16           │ │
│  │  Jinja2 templates   │       │                          │ │
│  │  Porta: 8000        │       │  Volume: postgres-data   │ │
│  └─────────────────────┘       └──────────────────────────┘ │
│           │                                                  │
└───────────│──────────────────────────────────────────────────┘
│ :8000
┌──────┴──────┐
│  Navegador  │
│  (usuário)  │
└─────────────┘

**Fluxo:**
1. Usuário acessa `http://localhost:8000`
2. FastAPI processa a requisição e consulta/grava no PostgreSQL
3. Jinja2 renderiza o HTML e retorna para o navegador
4. Dados persistem no volume `postgres-data`

**Operações CRUD implementadas:**
- Produtos: criar, listar, remover
- Clientes: criar, listar, remover
- Pedidos: criar, listar, remover

---

## Estrutura do Projeto
projeto/
├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── produtos.html
│       ├── clientes.html
│       └── pedidos.html
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── evidencias/

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DB_NAME` | `ecommerce` | Nome do banco |
| `DB_USER` | `postgres` | Usuário do PostgreSQL |
| `DB_PASSWORD` | `postgres` | Senha do PostgreSQL |
| `APP_PORT` | `8000` | Porta da aplicação |

---

## Portas Utilizadas

| Container | Porta interna | Porta externa | Serviço |
|---|---|---|---|
| `ecommerce-app` | 8000 | 8000 | Aplicação web |
| `ecommerce-db` | 5432 | — (interna) | PostgreSQL |

---

## Como Executar

### Pré-requisitos
- Docker instalado
- Docker Compose (incluso no Docker Desktop)

### 1. Clone o repositório

```bash
git clone https://github.com/tarugovv38-source/shopcloud-ecommerce.git
cd shopcloud-ecommerce
```

### 2. Inicie os containers

```bash
docker compose up --build
```

### 3. Acesse a aplicação

Abra o navegador em: **http://localhost:8000**

### 4. Parar os containers

```bash
# Para e mantém os dados
docker compose stop

# Para e remove containers (dados persistem)
docker compose down

# Remove tudo incluindo volume
docker compose down -v
```

---

## Comandos Úteis

```bash
# Ver containers rodando
docker ps

# Ver logs
docker compose logs app

# Listar volumes
docker volume ls

# Acessar o banco
docker exec -it ecommerce-db psql -U postgres -d ecommerce
```

---

## Instruções do Docker Compose

| Configuração | Descrição |
|---|---|
| `networks: ecommerce-net` | Rede bridge isolada |
| `volumes: postgres-data` | Persistência do PostgreSQL |
| `depends_on + healthcheck` | App aguarda banco estar pronto |
| `environment` | Variáveis injetadas nos containers |
| `restart: unless-stopped` | Reinicialização automática |

---

## DockerHub

```bash
docker pull tarugovv38-source/shopcloud-ecommerce:latest
```
