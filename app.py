from flask import Flask, request, jsonify, render_template
import psycopg2, os

app = Flask(__name__, static_folder="static", template_folder="templates")

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

# ---------- FRONTEND ----------
@app.route("/")
def index():
    return render_template("index.html")

# ---------- CLIENTES ----------
@app.route("/clientes", methods=["POST","GET"])
def clientes():
    c = conn()
    cur = c.cursor()

    if request.method == "POST":
        cur.execute(
            "INSERT INTO clientes (nome) VALUES (%s)",
            (request.json["nome"],)
        )
        c.commit()
        return {"ok": True}

    cur.execute("SELECT * FROM clientes")
    return jsonify(cur.fetchall())

# ---------- AGENDA ----------
@app.route("/agenda", methods=["POST","GET"])
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
from datetime import date
from flask import request, jsonify

# ABRIR CAIXA
@app.route("/abrir_caixa", methods=["POST"])
def abrir_caixa():
    abertura = request.json.get("abertura")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM caixa WHERE status='aberto'")
    if cur.fetchone():
        return jsonify({"erro": "Já existe um caixa aberto"}), 400

    cur.execute(
        "INSERT INTO caixa (data, abertura, status) VALUES (%s, %s, 'aberto') RETURNING id",
        (date.today(), abertura)
    )
    caixa_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"msg": "Caixa aberto", "caixa_id": caixa_id})


# ADICIONAR MOVIMENTAÇÃO
@app.route("/movimentacao", methods=["POST"])
def movimentacao():
    dados = request.json
    tipo = dados["tipo"]
    descricao = dados["descricao"]
    valor = dados["valor"]
    forma = dados.get("forma_pagamento")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM caixa WHERE status='aberto'")
    caixa = cur.fetchone()
    if not caixa:
        return jsonify({"erro": "Nenhum caixa aberto"}), 400

    cur.execute("""
        INSERT INTO movimentacoes (caixa_id, tipo, descricao, valor, forma_pagamento)
        VALUES (%s, %s, %s, %s, %s)
    """, (caixa[0], tipo, descricao, valor, forma))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"msg": "Movimentação registrada"})


# RESUMO DO CAIXA
@app.route("/resumo_caixa")
def resumo_caixa():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, abertura FROM caixa WHERE status='aberto'")
    caixa = cur.fetchone()
    if not caixa:
        return jsonify({"aberto": False})

    cur.execute("""
        SELECT tipo, SUM(valor)
        FROM movimentacoes
        WHERE caixa_id=%s
        GROUP BY tipo
    """, (caixa[0],))

    resumo = {row[0]: float(row[1]) for row in cur.fetchall()}

    cur.close()
    conn.close()

    return jsonify({
        "aberto": True,
        "abertura": float(caixa[1]),
        "entradas": resumo.get("entrada", 0),
        "saidas": resumo.get("saida", 0)
    })


# FECHAR CAIXA
@app.route("/fechar_caixa", methods=["POST"])
def fechar_caixa():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, abertura FROM caixa WHERE status='aberto'")
    caixa = cur.fetchone()
    if not caixa:
        return jsonify({"erro": "Nenhum caixa aberto"}), 400

    cur.execute("""
        SELECT 
        SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END),
        SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END)
        FROM movimentacoes WHERE caixa_id=%s
    """, (caixa[0],))

    entradas, saidas = cur.fetchone()
    saldo = (entradas or 0) - (saidas or 0)

    cur.execute(
        "UPDATE caixa SET fechamento=%s, status='fechado' WHERE id=%s",
        (saldo, caixa[0])
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"msg": "Caixa fechado", "saldo": float(saldo)})
from datetime import date, timedelta

# CADASTRAR PLANO
@app.route("/planos", methods=["POST"])
def criar_plano():
    dados = request.json
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO planos (nome, usos_totais, valor) VALUES (%s,%s,%s)",
        (dados["nome"], dados["usos"], dados["valor"])
    )

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Plano criado"})


# LISTAR PLANOS
@app.route("/planos")
def listar_planos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM planos")
    planos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(planos)


# VENDER PLANO AO CLIENTE
@app.route("/vender_plano", methods=["POST"])
def vender_plano():
    dados = request.json
    inicio = date.today()
    fim = inicio + timedelta(days=30)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """INSERT INTO cliente_planos 
        (cliente_id, plano_id, usos_restantes, data_inicio, data_fim)
        VALUES (%s,%s,
        (SELECT usos_totais FROM planos WHERE id=%s),
        %s,%s)""",
        (dados["cliente_id"], dados["plano_id"], dados["plano_id"], inicio, fim)
    )

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Plano vendido ao cliente"})
    from datetime import date, timedelta
from flask import request, jsonify

# CRIAR PLANO
@app.route("/planos", methods=["POST"])
def criar_plano():
    dados = request.json
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO planos (nome, usos_totais, valor) VALUES (%s,%s,%s)",
        (dados["nome"], dados["usos"], dados["valor"])
    )

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Plano criado com sucesso"})


# LISTAR PLANOS
@app.route("/planos")
def listar_planos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM planos")
    planos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(planos)


# VENDER PLANO
@app.route("/vender_plano", methods=["POST"])
def vender_plano():
    dados = request.json
    inicio = date.today()
    fim = inicio + timedelta(days=30)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cliente_planos
        (cliente_id, plano_id, usos_restantes, data_inicio, data_fim)
        VALUES (
            %s, %s,
            (SELECT usos_totais FROM planos WHERE id=%s),
            %s, %s
        )
    """, (dados["cliente_id"], dados["plano_id"], dados["plano_id"], inicio, fim))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Plano vendido ao cliente"})
