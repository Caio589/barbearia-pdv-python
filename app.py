from flask import Flask, render_template, request, redirect
from database import criar_tabelas, conectar

app = Flask(__name__)
criar_tabelas()

@app.route("/")
def home():
    con = conectar()
    c = con.cursor()

    c.execute("SELECT * FROM caixa ORDER BY id DESC")
    caixa = c.fetchall()

    c.execute("SELECT * FROM servicos")
    servicos = c.fetchall()

    c.execute("SELECT * FROM produtos")
    produtos = c.fetchall()

    c.execute("SELECT aberto FROM caixa_status WHERE id=1")
    aberto = c.fetchone()[0]

    con.close()

    return render_template(
        "index.html",
        caixa=caixa,
        servicos=servicos,
        produtos=produtos,
        aberto=aberto
    )

@app.route("/abrir_caixa", methods=["POST"])
def abrir_caixa():
    saldo = float(request.form["saldo"])
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
    c = con.cursor()
    c.execute("UPDATE caixa_status SET aberto=0")
    con.commit()
    con.close()
    return redirect("/")

@app.route("/venda", methods=["POST"])
def venda():
    descricao = request.form["descricao"]
    valor = float(request.form["valor"])
    pagamento = request.form["pagamento"]

    con = conectar()
    c = con.cursor()

    c.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES (?, ?, 'entrada', ?)
    """, (descricao, valor, pagamento))

    con.commit()
    con.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
