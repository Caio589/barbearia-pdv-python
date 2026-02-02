import psycopg2
import os

_conn = None  # conexão única

def get_db_connection():
    global _conn
    if _conn is None:
        _conn = psycopg2.connect(
            os.environ["DATABASE_URL"],
            sslmode="require"
        )
        criar_tabelas(_conn)
    return _conn


def criar_tabelas(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            telefone VARCHAR(30)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            valor NUMERIC(10,2) NOT NULL
        )
    """)

    conn.commit()
    cur.close()
