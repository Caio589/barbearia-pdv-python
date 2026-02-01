from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# ---------- CONEXÃO ----------
def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# ---------- CRIAR TABELAS ----------
def criar_tabelas():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

criar_tabelas()

# ---------- ROTAS ----------
@app.route("/")
def home():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes ORDER BY id DESC")
    clientes = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(clientes)

@app.route("/clientes", methods=["POST"])
def adicionar_cliente():
    dados = request.json
    nome = dados.get("nome")
    telefone = dados.get("telefone")

    if not nome:
        return {"erro": "Nome é obrigatório"}, 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clientes (nome, telefone) VALUES (%s, %s)",
        (nome, telefone)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"status": "cliente cadastrado"}

# ---------- START ----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
