import sqlite3

def conectar():
    return sqlite3.connect("barbearia.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # CLIENTES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        plano_id INTEGER
    )
    """)

    # SERVIÇOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL
    )
    """)

    # PRODUTOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL
    )
    """)

    # PLANOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        valor REAL NOT NULL
    )
    """)

    # RELAÇÃO PLANO x SERVIÇO
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plano_servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plano_id INTEGER,
        servico_id INTEGER
    )
    """)

    # CAIXA
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
