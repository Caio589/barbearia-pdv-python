import psycopg2
import psycopg2.extras
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def criar_tabelas():
    con = conectar()
    c = con.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT,
            plano_id INTEGER,
            saldo_plano INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            preco NUMERIC NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            preco NUMERIC NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS planos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            valor NUMERIC NOT NULL,
            limite INTEGER NOT NULL
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
        CREATE TABLE IF NOT EXISTS caixa_status (
            id INTEGER PRIMARY KEY,
            aberto INTEGER DEFAULT 0,
            saldo_inicial NUMERIC DEFAULT 0
        )
    """)

    c.execute("""
        INSERT INTO caixa_status (id, aberto)
        VALUES (1, 0)
        ON CONFLICT (id) DO NOTHING
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
        CREATE TABLE IF NOT EXISTS uso_plano (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER,
            servico_id INTEGER,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.commit()
    con.close()
