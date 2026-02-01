from flask import Flask, request, jsonify, render_template
import psycopg2, os

app = Flask(__name__, static_folder="static", template_folder="templates")

DATABASE_URL = os.getenv("DATABASE_URL")

def conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def criar_tabelas():
    c = conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS agenda (
        id SERIAL PRIMARY KEY,
        cliente TEXT,
        servico TEXT,
        data TEXT,
        hora TEXT
    );
    """)

    c.commit()
    cur.close()
    c.close()

criar_tabelas()

# ---------- FRONTEND ----------
@app.route("/")
def index():
    return render_template("index.html")

# ---------- CLIENTES ----------
@app.route("/clientes", methods=["POST","GET"])
def clientes():
    c = conn()
    cur = c.cursor()

    if request.method == "POST":
        cur.execute(
            "INSERT INTO clientes (nome) VALUES (%s)",
            (request.json["nome"],)
        )
        c.commit()
        return {"ok": True}

    cur.execute("SELECT * FROM clientes")
    return jsonify(cur.fetchall())

# ---------- AGENDA ----------
@app.route("/agenda", methods=["POST","GET"])
def agenda():
    c = conn()
    cur = c.cursor()

    if request.method == "POST":
        d = request.json
        cur.execute("""
            INSERT INTO agenda (cliente, servico, data, hora)
            VALUES (%s,%s,%s,%s)
        """,(d["cliente"],d["servico"],d["data"],d["hora"]))
        c.commit()
        return {"ok":True}

    cur.execute("SELECT * FROM agenda")
    return jsonify(cur.fetchall())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",5000)))
