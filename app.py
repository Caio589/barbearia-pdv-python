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
            dados = request.json
            cur.execute(
                "INSERT INTO clientes (nome, telefone) VALUES (%s, %s)",
                (dados["nome"], dados["telefone"])
            )
            conn.commit()
            return jsonify({"msg": "Cliente cadastrado com sucesso"})

        cur.execute("SELECT id, nome, telefone FROM clientes ORDER BY id DESC")
        clientes = cur.fetchall()
        return jsonify(clientes)

    except Exception as e:
        print("ERRO /clientes:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cur.close()

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
                "INSERT INTO servicos (nome, valor) VALUES (%s, %s)",
                (dados["nome"], dados["valor"])
            )
            conn.commit()
            return jsonify({"msg": "Serviço cadastrado com sucesso"})

        cur.execute("SELECT id, nome, valor FROM servicos ORDER BY id DESC")
        servicos = cur.fetchall()
        return jsonify(servicos)

    except Exception as e:
        print("ERRO /servicos:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cur.close()

# ======================
# START
# ======================
if __name__ == "__main__":
    app.run(debug=True)
