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
        criar_tabelas_e_colunas(conn)
        _tabelas_criadas = True

    return conn


def criar_tabelas_e_colunas(conn):
    cur = conn.cursor()

    # ======================
    # CLIENTES
    # ======================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100),
            telefone VARCHAR(30)
        )
    """)

    # ======================
    # SERVICOS
    # ======================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100)
        )
    """)

    # adiciona coluna valor se não existir
    cur.execute("""
        ALTER TABLE servicos
        ADD COLUMN IF NOT EXISTS valor NUMERIC(10,2)
    """)

    # ======================
    # CAIXA
    # ======================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS caixa (
            id SERIAL PRIMARY KEY,
            aberto BOOLEAN DEFAULT TRUE
        )
    """)

    # adiciona coluna abertura se não existir
    cur.execute("""
        ALTER TABLE caixa
        ADD COLUMN IF NOT EXISTS abertura NUMERIC(10,2)
    """)

    # ======================
    # MOVIMENTACOES
    # ======================
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
