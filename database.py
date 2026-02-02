import psycopg2
import os

def get_db_connection():
    conn = psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode="require"
    )
    criar_tabelas(conn)
    return conn


def criar_tabelas(conn):
    cur = conn.cursor()

    # CLIENTES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            telefone VARCHAR(30)
        )
    """)

    # SERVIÇOS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            valor NUMERIC(10,2) NOT NULL
        )
    """)

    conn.commit()
    cur.close()
