import sqlite3

def conectar():
    return sqlite3.connect("barbearia.db", check_same_thread=False)

def criar_tabelas():
    con = conectar()
    c = con.cursor()

    # CLIENTES COM SALDO DE PLANO
    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT,
        plano_id INTEGER,
        saldo_plano INTEGER DEFAULT 0
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

    # PLANO COM LIMITE
    c.execute("""
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        valor REAL,
        limite INTEGER
    )
    """)

    # HISTÓRICO DE USO DO PLANO
    c.execute("""
    CREATE TABLE IF NOT EXISTS uso_plano (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        servico_id INTEGER,
        data DATETIME DEFAULT CURRENT_TIMESTAMP
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
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        hora TEXT,
        cliente_id INTEGER,
        servico_id INTEGER
    )
    """)
