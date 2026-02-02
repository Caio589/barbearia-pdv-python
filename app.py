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

    if request.method == "POST":
        dados = request.json
        cur.execute(
            "INSERT INTO clientes (nome, telefone) VALUES (%s,%s)",
            (dados["nome"], dados["telefone"])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"msg": "Cliente cadastrado"})

    cur.execute("SELECT id, nome, telefone FROM clientes ORDER BY id DESC")
    lista = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(lista)

# ======================
# SERVIÇOS
# ======================
@app.route("/servicos", methods=["GET", "POST"])
def servicos():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        dados = request.json
        cur.execute(
            "INSERT INTO servicos (nome, valor) VALUES (%s,%s)",
            (dados["nome"], dados["valor"])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"msg": "Serviço cadastrado"})

    cur.execute("SELECT id, nome, valor FROM servicos ORDER BY id DESC")
    lista = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(lista)

if __name__ == "__main__":
    app.run(debug=True)
