 import psycopg2
import os

_tabelas_criadas = False

def get_db_connection():
    global _tabelas_criadas

    conn = psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode="require"
    )

    if not _tabelas_criadas:
        criar_tabelas(conn)
        _tabelas_criadas = True

    return conn


def criar_tabelas(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100),
            telefone VARCHAR(30)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100),
            valor NUMERIC(10,2)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS caixa (
            id SERIAL PRIMARY KEY,
            aberto BOOLEAN DEFAULT TRUE,
            abertura NUMERIC(10,2),
            data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id SERIAL PRIMARY KEY,
            caixa_id INTEGER,
            valor NUMERIC(10,2),
            forma_pagamento VARCHAR(20),
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
