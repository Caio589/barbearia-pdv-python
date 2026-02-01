from flask import Flask, render_template, request, redirect, jsonify, send_file
from database import criar_tabelas, conectar
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
criar_tabelas()

# ================= HOME =================
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

    # -------- AGENDA --------
    c.execute("""
        SELECT a.id, a.data, a.hora, c.nome, s.nome
        FROM agenda a
        JOIN clientes c ON c.id = a.cliente_id
        JOIN servicos s ON s.id = a.servico_id
        ORDER BY a.data, a.hora
    """)
    agenda = c.fetchall()

    # -------- RELATÓRIO --------
    mes = datetime.now().strftime("%Y-%m")

    def total(p):
        c.execute("""
            SELECT IFNULL(SUM(valor),0)
            FROM caixa
            WHERE tipo='entrada'
              AND pagamento=?
              AND strftime('%Y-%m', data)=?
        """, (p, mes))
        return c.fetchone()[0]

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

# ================= CAIXA =================
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

# ================= API PREÇO =================
@app.route("/preco/<tipo>/<int:item_id>")
def preco(tipo, item_id):
    con = conectar()
    c = con.cursor()

    if tipo == "servico":
        c.execute("SELECT preco FROM servicos WHERE id=?", (item_id,))
    else:
        c.execute("SELECT preco FROM produtos WHERE id=?", (item_id,))

    row = c.fetchone()
    con.close()
    return jsonify(row[0] if row else 0)

# ================= VENDA =================
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

# ================= CADASTROS =================
@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    nome = request.form.get("nome")
    telefone = request.form.get("telefone", "")

    if not nome:
        return redirect("/")

    con = conectar()
    con.cursor().execute(
        "INSERT INTO clientes (nome, telefone) VALUES (?,?)",
        (nome, telefone)
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/add_servico", methods=["POST"])
def add_servico():
    nome = request.form.get("nome")
    preco = request.form.get("preco")

    if not nome or not preco:
        return redirect("/")

    try:
        preco = float(preco.replace(",", "."))
    except:
        preco = 0.0

    con = conectar()
    con.cursor().execute(
        "INSERT INTO servicos (nome, preco) VALUES (?,?)",
        (nome, preco)
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/add_produto", methods=["POST"])
def add_produto():
    nome = request.form.get("nome")
    preco = request.form.get("preco")

    if not nome or not preco:
        return redirect("/")

    try:
        preco = float(preco.replace(",", "."))
    except:
        preco = 0.0

    con = conectar()
    con.cursor().execute(
        "INSERT INTO produtos (nome, preco) VALUES (?,?)",
        (nome, preco)
    )
    con.commit()
    con.close()
    return redirect("/")

# ================= AGENDA =================
@app.route("/add_agenda", methods=["POST"])
def add_agenda():
    data = request.form.get("data")
    hora = request.form.get("hora")
    cliente = request.form.get("cliente")
    servico = request.form.get("servico")

    if not data or not hora or not cliente or not servico:
        return redirect("/")

    con = conectar()
    con.cursor().execute(
        "INSERT INTO agenda (data, hora, cliente_id, servico_id) VALUES (?,?,?,?)",
        (data, hora, cliente, servico)
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/del_agenda/<int:id>")
def del_agenda(id):
    con = conectar()
    con.cursor().execute("DELETE FROM agenda WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect("/")

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
        AND strftime('%Y-%m', data)=?
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
        pdf.drawString(50, y, f"{d[3][:10]} | {d[0]} | R$ {d[1]:.2f} | {d[2]}")
        y -= 14
        if y < 40:
            pdf.showPage()
            y = h - 50

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_mensal.pdf")

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/add_plano", methods=["POST"])
def add_plano():
    nome = request.form.get("nome")
    valor = request.form.get("valor")
    limite = request.form.get("limite", "0")

    if not nome or not valor:
        return redirect("/")

    try:
        valor = float(valor.replace(",", "."))
    except:
        valor = 0.0

    try:
        limite = int(limite)
    except:
        limite = 0

    con = conectar()
    con.cursor().execute(
        "INSERT INTO planos (nome, valor, limite) VALUES (?,?,?)",
        (nome, valor, limite)
    )
    con.commit()
    con.close()
    return redirect("/")
