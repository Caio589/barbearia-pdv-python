from flask import Flask, render_template, request, jsonify
from database import get_db_connection

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

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
        "INSERT INTO caixa (abertura, aberto) VALUES (%s, true)",
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
        VALUES (%s, %s, %s)
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

    resultado = {"abertura": float(abertura)}

    for forma, valor in totais:
        resultado[forma] = float(valor)
        total += float(valor)

    cur.execute("UPDATE caixa SET aberto=false WHERE id=%s", (caixa_id,))
    conn.commit()

    cur.close()
    conn.close()

    resultado["total"] = total
    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True)
