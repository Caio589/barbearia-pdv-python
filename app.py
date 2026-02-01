from flask import Flask, render_template, request, redirect, jsonify
from database import criar_tabelas, conectar

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

    c.execute("SELECT aberto FROM caixa_status WHERE id=1")
    aberto = c.fetchone()[0]

    con.close()

    return render_template(
        "index.html",
        clientes=clientes,
        servicos=servicos,
        produtos=produtos,
        aberto=aberto
    )

# -------- CAIXA --------
@app.route("/abrir_caixa", methods=["POST"])
def abrir_caixa():
    saldo = float(request.form.get("saldo", "0").replace(",", "."))
    con = conectar()
    c = con.cursor()
    c.execute("UPDATE caixa_status SET aberto=1, saldo_inicial=?", (saldo,))
    c.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES ('Abertura de Caixa', ?, 'entrada', 'Dinheiro')
    """, (saldo,))
    con.commit()
    con.close()
    return redirect("/")

@app.route("/fechar_caixa")
def fechar_caixa():
    con = conectar()
    con.cursor().execute("UPDATE caixa_status SET aberto=0")
    con.commit()
    con.close()
    return redirect("/")

# -------- API PREÇO --------
@app.route("/preco/<tipo>/<int:id>")
def preco(tipo, id):
    con = conectar()
    c = con.cursor()

    if tipo == "servico":
        c.execute("SELECT preco FROM servicos WHERE id=?", (id,))
    else:
        c.execute("SELECT preco FROM produtos WHERE id=?", (id,))

    preco = c.fetchone()[0]
    con.close()
    return jsonify(preco)

# -------- VENDA --------
@app.route("/venda", methods=["POST"])
def venda():
    tipo = request.form["tipo"]
    item_id = int(request.form["item"])
    pagamento = request.form["pagamento"]

    con = conectar()
    c = con.cursor()

    c.execute("SELECT aberto FROM caixa_status WHERE id=1")
    if c.fetchone()[0] != 1:
        con.close()
        return redirect("/")

    if tipo == "servico":
        c.execute("SELECT nome, preco FROM servicos WHERE id=?", (item_id,))
    else:
        c.execute("SELECT nome, preco FROM produtos WHERE id=?", (item_id,))

    nome, preco = c.fetchone()

    c.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES (?, ?, 'entrada', ?)
    """, (f"{tipo.title()}: {nome}", preco, pagamento))

    con.commit()
    con.close()
    return redirect("/")
