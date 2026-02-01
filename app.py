from flask import Flask, render_template, request, redirect, jsonify, send_file
from database import criar_tabelas, conectar
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os

app = Flask(__name__)

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
    aberto = c.fetchone()["aberto"]

    c.execute("""
        SELECT a.id, a.data, a.hora,
               cl.nome AS cliente,
               s.nome AS servico
        FROM agenda a
        JOIN clientes cl ON cl.id = a.cliente_id
        JOIN servicos s ON s.id = a.servico_id
        ORDER BY a.data, a.hora
    """)
    agenda = c.fetchall()

    mes = datetime.now().strftime("%Y-%m")

    def total(pag):
        c.execute("""
            SELECT COALESCE(SUM(valor),0) AS total
            FROM caixa
            WHERE tipo='entrada'
              AND pagamento=%s
              AND TO_CHAR(data,'YYYY-MM')=%s
        """, (pag, mes))
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

# ================= CAIXA =================
@app.route("/abrir_caixa", methods=["POST"])
def abrir_caixa():
    saldo = float(request.form.get("saldo", "0").replace(",", "."))
    con = conectar()
    c = con.cursor()
    c.execute("UPDATE caixa_status SET aberto=1, saldo_inicial=%s", (saldo,))
    c.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES ('Abertura de Caixa', %s, 'entrada', 'Dinheiro')
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

# ================= VENDA =================
@app.route("/venda", methods=["POST"])
def venda():
    tipo = request.form.get("tipo")
    item = request.form.get("item")
    pagamento = request.form.get("pagamento", "Dinheiro")

    con = conectar()
    c = con.cursor()

    c.execute("SELECT aberto FROM caixa_status WHERE id=1")
    if c.fetchone()["aberto"] != 1:
        con.close()
        return redirect("/")

    if tipo == "servico":
        c.execute("SELECT nome, preco FROM servicos WHERE id=%s", (item,))
    else:
        c.execute("SELECT nome, preco FROM produtos WHERE id=%s", (item,))

    r = c.fetchone()
    c.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES (%s,%s,'entrada',%s)
    """, (f"{tipo}: {r['nome']}", r["preco"], pagamento))

    con.commit()
    con.close()
    return redirect("/")

# ================= CADASTROS =================
@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO clientes (nome, telefone) VALUES (%s,%s)",
        (request.form["nome"], request.form.get("telefone",""))
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/add_servico", methods=["POST"])
def add_servico():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO servicos (nome, preco) VALUES (%s,%s)",
        (request.form["nome"], float(request.form["preco"].replace(",",".")))
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/add_produto", methods=["POST"])
def add_produto():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO produtos (nome, preco) VALUES (%s,%s)",
        (request.form["nome"], float(request.form["preco"].replace(",",".")))
    )
    con.commit()
    con.close()
    return redirect("/")

# ================= AGENDA =================
@app.route("/add_agenda", methods=["POST"])
def add_agenda():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO agenda (data,hora,cliente_id,servico_id) VALUES (%s,%s,%s,%s)",
        (request.form["data"], request.form["hora"],
         request.form["cliente"], request.form["servico"])
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/del_agenda/<int:id>")
def del_agenda(id):
    con = conectar()
    con.cursor().execute("DELETE FROM agenda WHERE id=%s", (id,))
    con.commit()
    con.close()
    return redirect("/")

# ================= PLANOS =================
@app.route("/add_plano", methods=["POST"])
def add_plano():
    con = conectar()
    con.cursor().execute(
        "INSERT INTO planos (nome, valor, limite) VALUES (%s,%s,%s)",
        (request.form["nome"],
         float(request.form["valor"].replace(",",".")),
         int(request.form.get("limite",0)))
    )
    con.commit()
    con.close()
    return redirect("/")

@app.route("/ativar_plano", methods=["POST"])
def ativar_plano():
    con = conectar()
    c = con.cursor()

    cliente = request.form["cliente"]
    plano = request.form["plano"]
    pagamento = request.form.get("pagamento","Dinheiro")

    c.execute("SELECT nome, valor, limite FROM planos WHERE id=%s",(plano,))
    p = c.fetchone()
    c.execute("SELECT nome FROM clientes WHERE id=%s",(cliente,))
    cl = c.fetchone()

    c.execute("""
        UPDATE clientes
        SET plano_id=%s, saldo_plano=%s
        WHERE id=%s
    """,(plano,p["limite"],cliente))

    c.execute("""
        INSERT INTO caixa (descricao,valor,tipo,pagamento)
        VALUES (%s,%s,'entrada',%s)
    """,(f"Plano {p['nome']} - {cl['nome']}",p["valor"],pagamento))

    con.commit()
    con.close()
    return redirect("/")

@app.route("/usar_plano", methods=["POST"])
def usar_plano():
    con = conectar()
    c = con.cursor()

    cliente = request.form["cliente"]
    servico = request.form["servico"]

    c.execute("SELECT saldo_plano FROM clientes WHERE id=%s",(cliente,))
    if c.fetchone()["saldo_plano"] <= 0:
        con.close()
        return redirect("/")

    c.execute("""
        INSERT INTO uso_plano (cliente_id,servico_id)
        VALUES (%s,%s)
    """,(cliente,servico))

    c.execute("""
        UPDATE clientes SET saldo_plano = saldo_plano - 1
        WHERE id=%s
    """,(cliente,))

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
        SELECT descricao,valor,pagamento,data
        FROM caixa
        WHERE tipo='entrada'
        AND TO_CHAR(data,'YYYY-MM')=%s
    """,(mes,))
    dados = c.fetchall()
    con.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    y = A4[1] - 80

    pdf.setFont("Helvetica-Bold",16)
    pdf.drawString(50,y,"Relatório Mensal")
    y -= 30
    pdf.setFont("Helvetica",10)

    for d in dados:
        pdf.drawString(50,y,f"{d['data']:%Y-%m-%d} | {d['descricao']} | R$ {d['valor']} | {d['pagamento']}")
        y -= 14

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio.pdf")

# ================= START =================
if __name__ == "__main__":
    criar_tabelas()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
