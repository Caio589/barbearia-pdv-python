from flask import Flask, render_template, request, jsonify
from database import get_db_connection

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# ======================
# CLIENTES
# ======================
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if request.method == "POST":
            dados = request.json
            cur.execute(
                "INSERT INTO clientes (nome, telefone) VALUES (%s,%s)",
                (dados["nome"], dados["telefone"])
            )
            conn.commit()
            return jsonify({"msg": "Cliente cadastrado"})

        cur.execute("SELECT id, nome, telefone FROM clientes ORDER BY id DESC")
        return jsonify(cur.fetchall())

    finally:
        cur.close()
        conn.close()

# ======================
# SERVIÇOS
# ======================
@app.route("/servicos", methods=["GET", "POST"])
def servicos():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if request.method == "POST":
            dados = request.json
            cur.execute(
                "INSERT INTO servicos (nome, valor) VALUES (%s,%s)",
                (dados["nome"], dados["valor"])
            )
            conn.commit()
            return jsonify({"msg": "Serviço cadastrado"})

        cur.execute("SELECT id, nome, valor FROM servicos ORDER BY id DESC")
        return jsonify(cur.fetchall())

    finally:
        cur.close()
        conn.close()

# ======================
# CAIXA
# ======================
@app.route("/abrir_caixa", methods=["POST"])
def abrir_caixa():
    conn = get_db_connection()
    cur = conn.cursor()

    valor = request.json["valor"]

    cur.execute("SELECT id FROM caixa WHERE aberto=true")
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"msg": "Já existe um caixa aberto"})

    cur.execute(
        "INSERT INTO caixa (abertura, aberto) VALUES (%s,true)",
        (valor,)
    )
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({"msg": "Caixa aberto"})

@app.route("/movimentacao", methods=["POST"])
def movimentacao():
    conn = get_db_connection()
    cur = conn.cursor()

    dados = request.json

    cur.execute("SELECT id FROM caixa WHERE aberto=true")
    caixa = cur.fetchone()
    if not caixa:
        cur.close()
        conn.close()
        return jsonify({"msg": "Nenhum caixa aberto"})

    cur.execute("""
        INSERT INTO movimentacoes (caixa_id, valor, forma_pagamento)
        VALUES (%s,%s,%s)
    """, (caixa[0], dados["valor"], dados["forma"]))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Entrada registrada"})

@app.route("/fechar_caixa")
def fechar_caixa():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, abertura FROM caixa WHERE aberto=true")
    caixa = cur.fetchone()
    if not caixa:
        cur.close()
        conn.close()
        return jsonify({"msg": "Nenhum caixa aberto"})

    caixa_id, abertura = caixa

    cur.execute("""
        SELECT forma_pagamento, SUM(valor)
        FROM movimentacoes
        WHERE caixa_id=%s
        GROUP BY forma_pagamento
    """, (caixa_id,))

    totais = cur.fetchall()
    total = float(abertura)
    resumo = {"abertura": float(abertura)}

    for forma, valor in totais:
        resumo[forma] = float(valor)
        total += float(valor)

    cur.execute("UPDATE caixa SET aberto=false WHERE id=%s", (caixa_id,))
    conn.commit()

    cur.close()
    conn.close()

    resumo["total"] = total
    return jsonify(resumo)

if __name__ == "__main__":
    app.run(debug=True)
