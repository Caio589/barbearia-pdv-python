from flask import Flask, render_template, request, jsonify
from database import get_db_connection

app = Flask(__name__)

# ======================
# HOME
# ======================
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
            dados = request.get_json()
            cur.execute(
                "INSERT INTO clientes (nome, telefone) VALUES (%s,%s)",
                (dados["nome"], dados["telefone"])
            )
            conn.commit()
            return jsonify({"msg": "Cliente cadastrado"})

        cur.execute("SELECT id, nome, telefone FROM clientes ORDER BY id DESC")
        return jsonify(cur.fetchall())

    except Exception as e:
        print("ERRO /clientes:", e)
        return jsonify([])

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
            dados = request.get_json()
            cur.execute(
                "INSERT INTO servicos (nome, valor) VALUES (%s,%s)",
                (dados["nome"], dados["valor"])
            )
            conn.commit()
            return jsonify({"msg": "Serviço cadastrado"})

        cur.execute("SELECT id, nome, valor FROM servicos ORDER BY id DESC")
        return jsonify(cur.fetchall())

    except Exception as e:
        print("ERRO /servicos:", e)
        return jsonify([])

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

    try:
        dados = request.get_json(silent=True)
        if not dados or "valor" not in dados:
            return jsonify({"msg": "Valor de abertura inválido"}), 400

        # 🔥 CONVERSÃO IMPORTANTE
        valor = float(dados["valor"])

        cur.execute("SELECT id FROM caixa WHERE aberto=true")
        if cur.fetchone():
            return jsonify({"msg": "Já existe um caixa aberto"})

        cur.execute(
            "INSERT INTO caixa (abertura, aberto) VALUES (%s, true)",
            (valor,)
        )
        conn.commit()

        return jsonify({"msg": "Caixa aberto com sucesso"})

    except Exception as e:
        print("ERRO /abrir_caixa:", e)
        return jsonify({"msg": "Erro ao abrir caixa"}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/movimentacao", methods=["POST"])
def movimentacao():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        dados = request.get_json()

        cur.execute("SELECT id FROM caixa WHERE aberto=true")
        caixa = cur.fetchone()
        if not caixa:
            return jsonify({"msg": "Nenhum caixa aberto"})

        cur.execute("""
            INSERT INTO movimentacoes (caixa_id, valor, forma_pagamento)
            VALUES (%s,%s,%s)
        """, (caixa[0], dados["valor"], dados["forma"]))

        conn.commit()
        return jsonify({"msg": "Movimentação registrada"})

    except Exception as e:
        print("ERRO /movimentacao:", e)
        return jsonify({"msg": "Erro na movimentação"})

    finally:
        cur.close()
        conn.close()


@app.route("/fechar_caixa")
def fechar_caixa():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, abertura FROM caixa WHERE aberto=true")
        caixa = cur.fetchone()
        if not caixa:
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

        resumo["total"] = total
        return jsonify(resumo)

    except Exception as e:
        print("ERRO /fechar_caixa:", e)
        return jsonify({"msg": "Erro ao fechar caixa"})

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
    # ======================
# PLANOS
# ======================
@app.route("/planos", methods=["GET", "POST"])
def planos():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if request.method == "POST":
            dados = request.get_json()
            cur.execute(
                "INSERT INTO planos (nome, valor, quantidade) VALUES (%s,%s,%s)",
                (dados["nome"], dados["valor"], dados["quantidade"])
            )
            conn.commit()
            return jsonify({"msg": "Plano criado com sucesso"})

        cur.execute("SELECT id, nome, valor, quantidade FROM planos ORDER BY id DESC")
        return jsonify(cur.fetchall())

    except Exception as e:
        print("ERRO /planos:", e)
        return jsonify([])

    # ======================
# PRODUTOS
# ======================
@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if request.method == "POST":
            dados = request.get_json()
            cur.execute(
                "INSERT INTO produtos (nome, valor, estoque) VALUES (%s,%s,%s)",
                (dados["nome"], dados["valor"], dados["estoque"])
            )
            conn.commit()
            return jsonify({"msg": "Produto cadastrado com sucesso"})

        cur.execute("SELECT id, nome, valor, estoque FROM produtos ORDER BY id DESC")
        return jsonify(cur.fetchall())

    except Exception as e:
        print("ERRO /produtos:", e)
        return jsonify([])

    finally:
        cur.close()
        conn.close()

    finally:
        cur.close()
        conn.close()

