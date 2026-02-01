from flask import Flask, render_template, request, redirect, jsonify, send_file
from database import criar_tabelas, conectar
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os

app = Flask(__name__)

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
    aberto = c.fetchone()["aberto"]

    c.execute("""
        SELECT a.id, a.data, a.hora, c.nome AS cliente, s.nome AS servico
        FROM agenda a
        JOIN clientes c ON c.id = a.cliente_id
        JOIN servicos s ON s.id = a.servico_id
        ORDER BY a.data, a.hora
    """)
    agenda = c.fetchall()

    mes = datetime.now().strftime("%Y-%m")

    def total(p):
        c.execute("""
            SELECT COALESCE(SUM(valor), 0) AS total
            FROM caixa
            WHERE tipo='entrada'
              AND pagamento=%s
              AND TO_CHAR(data, 'YYYY-MM')=%s
        """, (p, mes))
        return c.fetchone()["total"]

    total_dinheiro = total("Dinheiro")
    total_pix = total("Pix")
    total_cartao = total("Cartão")
    total_mes = total_dinheiro + total_pix + total_cartao

    con.close()

    return render_template(
        "index.html",
        clientes=clientes,
        servicos=servicos,
        produtos=produtos,
        planos=planos,
        caixa=caixa,
        agenda=agenda,
        aberto=aberto,
        total_dinheiro=total_dinheiro,
        total_pix=total_pix,
        total_cartao=total_cartao,
        total_mes=total_mes
    )

# ================= PDF =================
@app.route("/relatorio_pdf")
def relatorio_pdf():
    con = conectar()
    c = con.cursor()

    mes = datetime.now().strftime("%Y-%m")
    c.execute("""
        SELECT descricao, valor, pagamento, data
        FROM caixa
        WHERE tipo='entrada'
        AND TO_CHAR(data, 'YYYY-MM')=%s
    """, (mes,))
    dados = c.fetchall()
    con.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, h - 50, "Relatório Mensal - Barbearia")

    y = h - 90
    pdf.setFont("Helvetica", 10)
    for d in dados:
        pdf.drawString(
            50,
            y,
            f"{d['data']:%Y-%m-%d} | {d['descricao']} | R$ {float(d['valor']):.2f} | {d['pagamento']}"
        )
        y -= 14
        if y < 40:
            pdf.showPage()
            y = h - 50

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_mensal.pdf")

# ================= START =================
if __name__ == "__main__":
    criar_tabelas()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
