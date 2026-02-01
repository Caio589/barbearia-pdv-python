from flask import Flask, request, jsonify
import psycopg2, os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def criar_tabelas():
    c = conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        preco NUMERIC
    );

    CREATE TABLE IF NOT EXISTS servicos (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        preco NUMERIC
    );

    CREATE TABLE IF NOT EXISTS planos (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        valor NUMERIC,
        quantidade INT
    );

    CREATE TABLE IF NOT EXISTS clientes_planos (
        id SERIAL PRIMARY KEY,
        cliente_id INT,
        saldo INT
    );

    CREATE TABLE IF NOT EXISTS caixa (
        id SERIAL PRIMARY KEY,
        aberto BOOLEAN DEFAULT FALSE,
        total NUMERIC DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS vendas (
        id SERIAL PRIMARY KEY,
        descricao TEXT,
        valor NUMERIC
    );

    CREATE TABLE IF NOT EXISTS agenda (
        id SERIAL PRIMARY KEY,
        cliente TEXT,
        servico TEXT,
        data TEXT,
        hora TEXT
    );
    """)

    c.commit()
    cur.close()
    c.close()

criar_tabelas()

# ---------- CLIENTES ----------
@app.route("/clientes", methods=["GET","POST"])
def clientes():
    c = conn()
    cur = c.cursor()

    if request.method == "POST":
        nome = request.json["nome"]
        cur.execute("INSERT INTO clientes (nome) VALUES (%s)", (nome,))
        c.commit()
        return {"ok": True}

    cur.execute("SELECT * FROM clientes")
    dados = cur.fetchall()
    return jsonify(dados)

# ---------- PRODUTOS ----------
@app.route("/produtos", methods=["GET","POST"])
def produtos():
    c = conn()
    cur = c.cursor()

    if request.method == "POST":
        cur.execute("INSERT INTO produtos (nome, preco) VALUES (%s,%s)",
        (request.json["nome"], request.json["preco"]))
        c.commit()
        return {"ok": True}

    cur.execute("SELECT * FROM produtos")
    return jsonify(cur.fetchall())

# ---------- SERVIÇOS ----------
@app.route("/servicos", methods=["GET","POST"])
def servicos():
    c = conn()
    cur = c.cursor()

    if request.method == "POST":
        cur.execute("INSERT INTO servicos (nome, preco) VALUES (%s,%s)",
        (request.json["nome"], request.json["preco"]))
        c.commit()
        return {"ok": True}

    cur.execute("SELECT * FROM servicos")
    return jsonify(cur.fetchall())

# ---------- CAIXA ----------
@app.route("/caixa/abrir", methods=["POST"])
def abrir_caixa():
    c = conn()
    cur = c.cursor()
    cur.execute("INSERT INTO caixa (aberto) VALUES (true)")
    c.commit()
    return {"status":"caixa aberto"}

@app.route("/caixa/fechar", methods=["POST"])
def fechar_caixa():
    c = conn()
    cur = c.cursor()
    cur.execute("UPDATE caixa SET aberto=false")
    c.commit()
    return {"status":"caixa fechado"}

# ---------- VENDAS ----------
@app.route("/vender", methods=["POST"])
def vender():
    valor = request.json["valor"]
    desc = request.json["descricao"]

    c = conn()
    cur = c.cursor()

    cur.execute("INSERT INTO vendas (descricao, valor) VALUES (%s,%s)", (desc, valor))
    cur.execute("UPDATE caixa SET total = total + %s WHERE aberto=true", (valor,))

    c.commit()
    return {"ok":True}

# ---------- AGENDA ----------
@app.route("/agenda", methods=["GET","POST"])
def agenda():
    c = conn()
    cur = c.cursor()

    if request.method == "POST":
        d = request.json
        cur.execute("""
            INSERT INTO agenda (cliente, servico, data, hora)
            VALUES (%s,%s,%s,%s)
        """,(d["cliente"],d["servico"],d["data"],d["hora"]))
        c.commit()
        return {"ok":True}

    cur.execute("SELECT * FROM agenda")
    return jsonify(cur.fetchall())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",5000)))
