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

    cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM servicos ORDER BY id DESC")
    servicos = cursor.fetchall()

    conn.close()
    return render_template("index.html", clientes=clientes, servicos=servicos)

# -------- CLIENTES --------
@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    nome = request.form["nome"]
    telefone = request.form["telefone"]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, telefone) VALUES (?, ?)",
        (nome, telefone)
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_cliente/<int:id>")
def delete_cliente(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# -------- SERVIÇOS --------
@app.route("/add_servico", methods=["POST"])
def add_servico():
    nome = request.form["nome"]
    preco = request.form["preco"]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO servicos (nome, preco) VALUES (?, ?)",
        (nome, preco)
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_servico/<int:id>")
def delete_servico(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servicos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
