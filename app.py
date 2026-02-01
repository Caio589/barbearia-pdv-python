from flask import Flask, render_template, request, redirect, Response
import sqlite3
from datetime import date
from database import criar_tabelas
import csv

app = Flask(__name__)
criar_tabelas()

def conectar():
    return sqlite3.connect("barbearia.db")

@app.route("/")
def home():
    hoje = date.today().isoformat()
    mes = hoje[:7]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM servicos")
    servicos = cursor.fetchall()

    cursor.execute("SELECT * FROM caixa ORDER BY id DESC")
    caixa = cursor.fetchall()

    # totais por pagamento (dia)
    pagamentos = {}
    for p in ["Dinheiro", "Pix", "Cartão"]:
        cursor.execute("""
            SELECT IFNULL(SUM(valor),0)
            FROM caixa
            WHERE tipo='entrada' AND pagamento=? AND DATE(data)=?
        """, (p, hoje))
        pagamentos[p] = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        clientes=clientes,
        servicos=servicos,
        caixa=caixa,
        pagamentos=pagamentos
    )

# -------- VENDA --------
@app.route("/vender", methods=["POST"])
def vender():
    cliente_id = request.form["cliente"]
    servico_id = request.form["servico"]
    pagamento = request.form["pagamento"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nome, preco FROM servicos WHERE id=?", (servico_id,))
    servico = cursor.fetchone()

    cursor.execute("SELECT nome FROM clientes WHERE id=?", (cliente_id,))
    cliente = cursor.fetchone()

    descricao = f"{servico[0]} - {cliente[0]}"

    cursor.execute("""
        INSERT INTO vendas (cliente_id, servico_id, valor, pagamento)
        VALUES (?, ?, ?, ?)
    """, (cliente_id, servico_id, servico[1], pagamento))

    cursor.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES (?, ?, 'entrada', ?)
    """, (descricao, servico[1], pagamento))

    conn.commit()
    conn.close()
    return redirect("/")

# -------- EXPORTAR CSV --------
@app.route("/exportar_csv")
def exportar_csv():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT descricao, valor, pagamento, data FROM caixa")
    dados = cursor.fetchall()
    conn.close()

    def gerar():
        yield "Descricao,Valor,Pagamento,Data\n"
        for d in dados:
            yield f"{d[0]},{d[1]},{d[2]},{d[3]}\n"

    return Response(
        gerar(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=relatorio_caixa.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)
