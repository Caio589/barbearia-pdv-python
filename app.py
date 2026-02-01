import sqlite3

def conectar():
    return sqlite3.connect("barbearia.db", check_same_thread=False)

def criar_tabelas():
    con = conectar()
    c = con.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        valor REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS caixa_status (
        id INTEGER PRIMARY KEY,
        aberto INTEGER,
        saldo_inicial REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS caixa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT,
        valor REAL,
        tipo TEXT,
        pagamento TEXT,
        data DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
        INSERT OR IGNORE INTO caixa_status (id, aberto, saldo_inicial)
        VALUES (1, 0, 0)
    """)

    con.commit()
    con.close()
