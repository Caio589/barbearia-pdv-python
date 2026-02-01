from flask import Flask, render_template, request, redirect
import sqlite3
from database import criar_tabelas

app = Flask(__name__)
criar_tabelas()

def conectar():
    return sqlite3.connect("barbearia.db")

@app.route("/")
def home():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM servicos")
    servicos = cursor.fetchall()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    cursor.execute("SELECT * FROM planos")
    planos = cursor.fetchall()

    cursor.execute("SELECT * FROM caixa ORDER BY id DESC")
    caixa = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        clientes=clientes,
        servicos=servicos,
        produtos=produtos,
        planos=planos,
        caixa=caixa
    )

# -------- CLIENTES --------
@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, telefone) VALUES (?,?)",
        (request.form["nome"], request.form["telefone"])
    )
    conn.commit()
    conn.close()
    return redirect("/")

# -------- SERVIÇOS --------
@app.route("/add_servico", methods=["POST"])
def add_servico():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO servicos (nome, preco) VALUES (?,?)",
        (request.form["nome"], request.form["preco"])
    )
    conn.commit()
    conn.close()
    return redirect("/")

# -------- PRODUTOS --------
@app.route("/add_produto", methods=["POST"])
def add_produto():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, preco) VALUES (?,?)",
        (request.form["nome"], request.form["preco"])
    )
    conn.commit()
    conn.close()
    return redirect("/")

# -------- PLANOS --------
@app.route("/add_plano", methods=["POST"])
def add_plano():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO planos (nome, valor) VALUES (?,?)",
        (request.form["nome"], request.form["valor"])
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/ativar_plano", methods=["POST"])
def ativar_plano():
    cliente_id = request.form["cliente"]
    plano_id = request.form["plano"]
    pagamento = request.form["pagamento"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nome, valor FROM planos WHERE id=?", (plano_id,))
    plano = cursor.fetchone()

    cursor.execute("SELECT nome FROM clientes WHERE id=?", (cliente_id,))
    cliente = cursor.fetchone()

    cursor.execute(
        "UPDATE clientes SET plano_id=? WHERE id=?",
        (plano_id, cliente_id)
    )

    cursor.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES (?, ?, 'entrada', ?)
    """, (f"Plano {plano[0]} - {cliente[0]}", plano[1], pagamento))

    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
