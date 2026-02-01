import psycopg2
import os

DATABASE_URL = os.environ.getpostgresql://barbearia_db_k3da_user:Qc72SeyRPeoVVYvLDTRytgqJmkSbg5h2@dpg-d5vqldh4tr6s73a0dtr0-a/barbearia_db_k3da

def conectar():
    return psycopg2.connect(DATABASE_URL)

def criar_tabelas():
    con = conectar()
    c = con.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        telefone TEXT,
        plano_id INTEGER,
        saldo_plano INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS servicos (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        preco NUMERIC
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        preco NUMERIC
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS planos (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        valor NUMERIC,
        limite INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS uso_plano (
        id SERIAL PRIMARY KEY,
        cliente_id INTEGER,
        servico_id INTEGER,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS agenda (
        id SERIAL PRIMARY KEY,
        data DATE,
        hora TIME,
        cliente_id INTEGER,
        servico_id INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS caixa_status (
        id INTEGER PRIMARY KEY,
        aberto INTEGER,
        saldo_inicial NUMERIC
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS caixa (
        id SERIAL PRIMARY KEY,
        descricao TEXT,
        valor NUMERIC,
        tipo TEXT,
        pagamento TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    INSERT INTO caixa_status (id, aberto, saldo_inicial)
    VALUES (1, 0, 0)
    ON CONFLICT (id) DO NOTHING
    """)

    con.commit()
    con.close()
