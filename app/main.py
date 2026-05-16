from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import psycopg2
import psycopg2.extras
import os
import time

app = FastAPI(title="E-Commerce Dashboard")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Database ──────────────────────────────────────────────────────────────────

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "ecommerce"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def init_db():
    for attempt in range(10):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(120) NOT NULL,
                    descricao TEXT,
                    preco NUMERIC(10,2) NOT NULL,
                    estoque INTEGER DEFAULT 0,
                    criado_em TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(120) NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    telefone VARCHAR(20),
                    criado_em TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS pedidos (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER REFERENCES clientes(id),
                    produto_id INTEGER REFERENCES produtos(id),
                    quantidade INTEGER NOT NULL DEFAULT 1,
                    total NUMERIC(10,2),
                    status VARCHAR(30) DEFAULT 'pendente',
                    criado_em TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Banco inicializado com sucesso.")
            return
        except Exception as e:
            print(f"⏳ Aguardando banco... tentativa {attempt+1}/10 — {e}")
            time.sleep(3)
    raise RuntimeError("Não foi possível conectar ao banco de dados.")


@app.on_event("startup")
def startup():
    init_db()


# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch_all(query, params=()):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def execute(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()
    conn.close()


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/")
def index(request: Request):
    produtos = fetch_all("SELECT COUNT(*) AS total FROM produtos")[0]["total"]
    clientes = fetch_all("SELECT COUNT(*) AS total FROM clientes")[0]["total"]
    pedidos  = fetch_all("SELECT COUNT(*) AS total FROM pedidos")[0]["total"]
    receita  = fetch_all("SELECT COALESCE(SUM(total),0) AS total FROM pedidos WHERE status='pago'")[0]["total"]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_produtos": produtos,
        "total_clientes": clientes,
        "total_pedidos": pedidos,
        "receita_total": receita,
    })


# ── Produtos ──────────────────────────────────────────────────────────────────

@app.get("/produtos")
def produtos_list(request: Request):
    rows = fetch_all("SELECT * FROM produtos ORDER BY criado_em DESC")
    return templates.TemplateResponse("produtos.html", {"request": request, "produtos": rows})


@app.post("/produtos")
def produtos_create(
    nome: str = Form(...),
    descricao: str = Form(""),
    preco: float = Form(...),
    estoque: int = Form(0),
):
    execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque) VALUES (%s,%s,%s,%s)",
        (nome, descricao, preco, estoque),
    )
    return RedirectResponse("/produtos", status_code=303)


@app.post("/produtos/{produto_id}/delete")
def produtos_delete(produto_id: int):
    execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
    return RedirectResponse("/produtos", status_code=303)


# ── Clientes ──────────────────────────────────────────────────────────────────

@app.get("/clientes")
def clientes_list(request: Request):
    rows = fetch_all("SELECT * FROM clientes ORDER BY criado_em DESC")
    return templates.TemplateResponse("clientes.html", {"request": request, "clientes": rows})


@app.post("/clientes")
def clientes_create(
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(""),
):
    try:
        execute(
            "INSERT INTO clientes (nome, email, telefone) VALUES (%s,%s,%s)",
            (nome, email, telefone),
        )
    except Exception:
        pass
    return RedirectResponse("/clientes", status_code=303)


@app.post("/clientes/{cliente_id}/delete")
def clientes_delete(cliente_id: int):
    execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
    return RedirectResponse("/clientes", status_code=303)


# ── Pedidos ───────────────────────────────────────────────────────────────────

@app.get("/pedidos")
def pedidos_list(request: Request):
    rows = fetch_all("""
        SELECT p.id, c.nome AS cliente, pr.nome AS produto,
               p.quantidade, p.total, p.status, p.criado_em
        FROM pedidos p
        JOIN clientes c  ON c.id = p.cliente_id
        JOIN produtos pr ON pr.id = p.produto_id
        ORDER BY p.criado_em DESC
    """)
    clientes = fetch_all("SELECT id, nome FROM clientes ORDER BY nome")
    produtos = fetch_all("SELECT id, nome, preco FROM produtos ORDER BY nome")
    return templates.TemplateResponse("pedidos.html", {
        "request": request,
        "pedidos": rows,
        "clientes": clientes,
        "produtos": produtos,
    })


@app.post("/pedidos")
def pedidos_create(
    cliente_id: int = Form(...),
    produto_id: int = Form(...),
    quantidade: int = Form(1),
    status: str = Form("pendente"),
):
    preco = fetch_all("SELECT preco FROM produtos WHERE id=%s", (produto_id,))
    if preco:
        total = float(preco[0]["preco"]) * quantidade
        execute(
            "INSERT INTO pedidos (cliente_id, produto_id, quantidade, total, status) VALUES (%s,%s,%s,%s,%s)",
            (cliente_id, produto_id, quantidade, total, status),
        )
    return RedirectResponse("/pedidos", status_code=303)


@app.post("/pedidos/{pedido_id}/delete")
def pedidos_delete(pedido_id: int):
    execute("DELETE FROM pedidos WHERE id=%s", (pedido_id,))
    return RedirectResponse("/pedidos", status_code=303)
