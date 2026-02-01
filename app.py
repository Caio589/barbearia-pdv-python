from flask import Flask, render_template, request, redirect, jsonify, send_file
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

    # -------- RELATÓRIO MENSAL --------
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

# ---------------- API PREÇO ----------------
@app.route("/preco/<tipo>/<int:item_id>")
def preco(tipo, item_id):
    con = conectar()
    c = con.cursor()

    if tipo == "servico":
        c.execute("SELECT preco FROM servicos WHERE id=?", (item_id,))
    else:
        c.execute("SELECT preco FROM produtos WHERE id=?", (item_id,))

    preco = c.fetchone()[0]
    con.close()
    return jsonify(preco)

# ---------------- VENDA INTELIGENTE ----------------
@app.route("/venda", methods=["POST"])
def venda():
    tipo = request.form.get("tipo")
    item_id = request.form.get("item")
    pagamento = request.form.get("pagamento", "Dinheiro")

    if not tipo or not item_id:
        return redirect("/")

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

# ---------------- PLANOS ----------------
@app.route("/add_plano", methods=["POST"])
def add_plano():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO planos (nome, valor, limite) VALUES (?,?,?)",
        (
            request.form["nome"],
            request.form["valor"].replace(",", "."),
            request.form["limite"]
        )
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/ativar_plano", methods=["POST"])
def ativar_plano():
    cliente_id = request.form["cliente"]
    plano_id = request.form["plano"]
    pagamento = request.form["pagamento"]

    con = conectar()
    c = con.cursor()

    c.execute("SELECT nome, valor, limite FROM planos WHERE id=?", (plano_id,))
    plano = c.fetchone()

    c.execute("SELECT nome FROM clientes WHERE id=?", (cliente_id,))
    cliente = c.fetchone()

    c.execute("""
        UPDATE clientes
        SET plano_id=?, saldo_plano=?
        WHERE id=?
    """, (plano_id, plano[2], cliente_id))

    c.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES (?, ?, 'entrada', ?)
    """, (f"Plano {plano[0]} - {cliente[0]}", plano[1], pagamento))

    con.commit()
    con.close()
    return redirect("/")

@app.route("/usar_plano", methods=["POST"])
def usar_plano():
    cliente_id = request.form["cliente"]
    servico_id = request.form["servico"]

    con = conectar()
    c = con.cursor()

    c.execute("SELECT saldo_plano FROM clientes WHERE id=?", (cliente_id,))
    saldo = c.fetchone()[0]

    if saldo <= 0:
        con.close()
        return redirect("/")

    c.execute("""
        INSERT INTO uso_plano (cliente_id, servico_id)
        VALUES (?,?)
    """, (cliente_id, servico_id))

    c.execute("""
        UPDATE clientes
        SET saldo_plano = saldo_plano - 1
        WHERE id=?
    """, (cliente_id,))

    con.commit()
    con.close()
    return redirect("/")

# ---------------- PDF ----------------
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

    con.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, h-50, "Relatório Mensal - Barbearia")

    y = h-90
    pdf.setFont("Helvetica", 10)
    for d in dados:
        pdf.drawString(50, y, f"{d[3][:10]} | {d[0]} | R$ {d[1]:.2f} | {d[2]}")
        y -= 14
        if y < 40:
            pdf.showPage()
            y = h-50

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_mensal.pdf")
