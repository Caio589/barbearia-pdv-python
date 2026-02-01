import sqlite3

def conectar():
    return sqlite3.connect("barbearia.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT,
        plano_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        valor REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plano_servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plano_id INTEGER,
        servico_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uso_plano (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        servico_id INTEGER,
        data DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS caixa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT,
        valor REAL,
        tipo TEXT,
        pagamento TEXT,
        data DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
