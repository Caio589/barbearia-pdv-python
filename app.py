from flask import Flask, render_template, request, redirect
from database import criar_tabelas, conectar
from datetime import datetime

app = Flask(__name__)
criar_tabelas()

@app.route("/")
def home():
    con = conectar()
    c = con.cursor()

    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()

    c.execute("SELECT * FROM servicos")
    servicos = c.fetchall()

    c.execute("SELECT * FROM produtos")
    produtos = c.fetchall()

    c.execute("SELECT * FROM planos")
    planos = c.fetchall()

    c.execute("SELECT * FROM caixa ORDER BY id DESC")
    caixa = c.fetchall()

    c.execute("SELECT aberto FROM caixa_status WHERE id=1")
    aberto = c.fetchone()[0]

    # RELATÓRIO MENSAL
    mes = datetime.now().strftime("%Y-%m")

    def total_pagamento(tipo):
        c.execute("""
            SELECT IFNULL(SUM(valor),0)
            FROM caixa
            WHERE tipo='entrada'
            AND pagamento=?
            AND strftime('%Y-%m', data)=?
        """, (tipo, mes))
        return c.fetchone()[0]

    total_dinheiro = total_pagamento("Dinheiro")
    total_pix = total_pagamento("Pix")
    total_cartao = total_pagamento("Cartão")
    total_mes = total_dinheiro + total_pix + total_cartao

    con.close()

    return render_template(
        "index.html",
        clientes=clientes,
        servicos=servicos,
        produtos=produtos,
        planos=planos,
        caixa=caixa,
        aberto=aberto,
        total_dinheiro=total_dinheiro,
        total_pix=total_pix,
        total_cartao=total_cartao,
        total_mes=total_mes
    )

# ---------- CADASTROS ----------
@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO clientes (nome, telefone) VALUES (?,?)",
        (request.form["nome"], request.form["telefone"])
    )
    con.commit(); con.close()
    return redirect("/")

@app.route("/add_servico", methods=["POST"])
def add_servico():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO servicos (nome, preco) VALUES (?,?)",
        (request.form["nome"], request.form["preco"].replace(",", "."))
    )
    con.commit(); con.close()
    return redirect("/")

@app.route("/add_produto", methods=["POST"])
def add_produto():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO produtos (nome, preco) VALUES (?,?)",
        (request.form["nome"], request.form["preco"].replace(",", "."))
    )
    con.commit(); con.close()
    return redirect("/")

@app.route("/add_plano", methods=["POST"])
def add_plano():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO planos (nome, valor) VALUES (?,?)",
        (request.form["nome"], request.form["valor"].replace(",", "."))
    )
    con.commit(); con.close()
    return redirect("/")
