from flask import Flask, render_template, request, jsonify
import psycopg2
import os
from datetime import date, timedelta

app = Flask(__name__)

# =========================
# CONEXÃO COM O BANCO
# =========================
def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")

# =========================
# ROTAS BÁSICAS
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# CLIENTES (BASE)
# =========================
@app.route("/clientes")
def clientes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(dados)

# =========================
# PLANOS
# =========================
@app.route("/planos", methods=["GET", "POST"])
def planos():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        dados = request.json
        cur.execute(
            "INSERT INTO planos (nome, usos_totais, valor) VALUES (%s,%s,%s)",
            (dados["nome"], dados["usos"], dados["valor"])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"msg": "Plano criado com sucesso"})

    cur.execute("SELECT * FROM planos")
    planos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(planos)

# =========================
# VENDER PLANO
# =========================
@app.route("/vender_plano", methods=["POST"])
def vender_plano():
    dados = request.json
    inicio = date.today()
    fim = inicio + timedelta(days=30)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cliente_planos
        (cliente_id, plano_id, usos_restantes, data_inicio, data_fim, ativo)
        VALUES (
            %s, %s,
            (SELECT usos_totais FROM planos WHERE id=%s),
            %s, %s, true
        )
    """, (dados["cliente_id"], dados["plano_id"], dados["plano_id"], inicio, fim))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Plano vendido ao cliente"})

# =========================
# USAR PLANO
# =========================
@app.route("/usar_plano", methods=["POST"])
def usar_plano():
    cliente_id = request.json.get("cliente_id")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, plano_id, usos_restantes, data_fim
        FROM cliente_planos
        WHERE cliente_id=%s AND ativo=true
        ORDER BY data_fim DESC
        LIMIT 1
    """, (cliente_id,))
    plano = cur.fetchone()

    if not plano:
        return jsonify({"erro": "Cliente não possui plano ativo"}), 400

    cliente_plano_id, plano_id, usos, data_fim = plano

    if data_fim < date.today() or usos <= 0:
        cur.execute("UPDATE cliente_planos SET ativo=false WHERE id=%s", (cliente_plano_id,))
        conn.commit()
        return jsonify({"erro": "Plano vencido ou sem usos"}), 400

    cur.execute("""
        UPDATE cliente_planos
        SET usos_restantes = usos_restantes - 1
        WHERE id=%s
    """, (cliente_plano_id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "msg": "Plano utilizado com sucesso",
        "usos_restantes": usos - 1
    })

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(debug=True)
