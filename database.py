import sqlite3

def conectar():
    return sqlite3.connect("barbearia.db")

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

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

    c.execute("INSERT OR IGNORE INTO caixa_status (id, aberto, saldo_inicial) VALUES (1, 0, 0)")
    conn.commit()
    conn.close()
