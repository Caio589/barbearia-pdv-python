from flask import Flask, render_template, request, redirect, send_file
from database import criar_tabelas, conectar
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
criar_tabelas()

# ---------------- HOME ----------------
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

    def total_pagamento(p):
        c.execute("""
            SELECT IFNULL(SUM(valor),0)
            FROM caixa
            WHERE tipo='entrada'
              AND pagamento=?
              AND strftime('%Y-%m', data)=?
        """, (p, mes))
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

# ---------------- CAIXA ----------------
@app.route("/abrir_caixa", methods=["POST"])
def abrir_caixa():
    try:
        saldo = float(request.form.get("saldo", "0").replace(",", "."))
    except:
        saldo = 0.0

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

# ---------------- VENDA ----------------
@app.route("/venda", methods=["POST"])
def venda():
    descricao = request.form.get("descricao", "").strip()
    pagamento = request.form.get("pagamento", "Dinheiro")

    try:
        valor = float(request.form.get("valor", "0").replace(",", "."))
    except:
        return redirect("/")

    if valor <= 0 or descricao == "":
        return redirect("/")

    con = conectar()
    c = con.cursor()

    c.execute("SELECT aberto FROM caixa_status WHERE id=1")
    if c.fetchone()[0] != 1:
        con.close()
        return redirect("/")

    c.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES (?, ?, 'entrada', ?)
    """, (descricao, valor, pagamento))

    con.commit()
    con.close()
    return redirect("/")

# ---------------- CADASTROS ----------------
@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO clientes (nome, telefone) VALUES (?,?)",
        (request.form["nome"], request.form["telefone"])
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/add_servico", methods=["POST"])
def add_servico():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO servicos (nome, preco) VALUES (?,?)",
        (request.form["nome"], request.form["preco"].replace(",", "."))
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/add_produto", methods=["POST"])
def add_produto():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO produtos (nome, preco) VALUES (?,?)",
        (request.form["nome"], request.form["preco"].replace(",", "."))
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/add_plano", methods=["POST"])
def add_plano():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO planos (nome, valor) VALUES (?,?)",
        (request.form["nome"], request.form["valor"].replace(",", "."))
    )
    con.commit()
    con.close()
    return redirect("/")

# ---------------- PDF MENSAL ----------------
@app.route("/relatorio_pdf")
def relatorio_pdf():
    con = conectar()
    c = con.cursor()

    mes = datetime.now().strftime("%Y-%m")

    c.execute("""
        SELECT descricao, valor, pagamento, data
        FROM caixa
        WHERE tipo='entrada'
        AND strftime('%Y-%m', data)=?
    """, (mes,))
    dados = c.fetchall()

    c.execute("""
        SELECT pagamento, SUM(valor)
        FROM caixa
        WHERE tipo='entrada'
        AND strftime('%Y-%m', data)=?
        GROUP BY pagamento
    """, (mes,))
    totais = c.fetchall()

    con.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, altura - 50, "Relatório Mensal - Barbearia")

    y = altura - 90
    pdf.setFont("Helvetica", 10)

    for d in dados:
        pdf.drawString(50, y, f"{d[3][:10]} | {d[0]} | R$ {d[1]:.2f} | {d[2]}")
        y -= 14
        if y < 40:
            pdf.showPage()
            y = altura - 50

    pdf.showPage()
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, altura - 50, "Totais por pagamento")

    y = altura - 90
    pdf.setFont("Helvetica", 12)
    for t in totais:
        pdf.drawString(50, y, f"{t[0]}: R$ {t[1]:.2f}")
        y -= 20

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="relatorio_mensal.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)
