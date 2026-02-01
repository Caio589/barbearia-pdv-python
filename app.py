# -------- PLANOS --------
@app.route("/add_plano", methods=["POST"])
def add_plano():
    nome = request.form["nome"]
    valor = request.form["valor"]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO planos (nome, valor) VALUES (?, ?)",
        (nome, valor)
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_plano/<int:id>")
def delete_plano(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM planos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/ativar_plano", methods=["POST"])
def ativar_plano():
    cliente_id = request.form["cliente"]
    plano_id = request.form["plano"]
    pagamento = request.form["pagamento"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nome, valor FROM planos WHERE id=?", (plano_id,))
    plano = cursor.fetchone()

    cursor.execute("SELECT nome FROM clientes WHERE id=?", (cliente_id,))
    cliente = cursor.fetchone()

    # vincula plano ao cliente
    cursor.execute(
        "UPDATE clientes SET plano_id=? WHERE id=?",
        (plano_id, cliente_id)
    )

    # entrada no caixa
    descricao = f"Plano {plano[0]} - {cliente[0]}"
    cursor.execute("""
        INSERT INTO caixa (descricao, valor, tipo, pagamento)
        VALUES (?, ?, 'entrada', ?)
    """, (descricao, plano[1], pagamento))

    conn.commit()
    conn.close()
    return redirect("/")
