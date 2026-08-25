"""
database.py
Responsável pela conexão com o SQLite e criação das tabelas.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "financas.db"


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco de dados, com chaves estrangeiras ativadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    """Cria as tabelas do banco caso ainda não existam."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'corrente',
            saldo_inicial REAL NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subcategorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE CASCADE,
            UNIQUE (categoria_id, nome)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_id INTEGER NOT NULL,
            categoria_id INTEGER NOT NULL,
            subcategoria_id INTEGER,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            descricao TEXT,
            tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa')),
            FOREIGN KEY (conta_id) REFERENCES contas (id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE RESTRICT,
            FOREIGN KEY (subcategoria_id) REFERENCES subcategorias (id) ON DELETE SET NULL
        )
    """)

    # Migração: bancos criados antes da subcategoria_id existir ganham a coluna agora.
    try:
        cursor.execute("ALTER TABLE transacoes ADD COLUMN subcategoria_id INTEGER REFERENCES subcategorias(id) ON DELETE SET NULL")
    except sqlite3.OperationalError:
        pass  # coluna já existe

    conn.commit()
    conn.close()


def popular_categorias_padrao():
    """Insere um conjunto básico de categorias, caso a tabela esteja vazia."""
    categorias_padrao = [
        ("Salário", "receita"),
        ("Outras receitas", "receita"),
        ("Alimentação", "despesa"),
        ("Transporte", "despesa"),
        ("Moradia", "despesa"),
        ("Lazer", "despesa"),
        ("Saúde", "despesa"),
        ("Outras despesas", "despesa"),
    ]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categorias")
    total = cursor.fetchone()[0]

    if total == 0:
        cursor.executemany(
            "INSERT INTO categorias (nome, tipo) VALUES (?, ?)",
            categorias_padrao,
        )
        conn.commit()

    conn.close()


if __name__ == "__main__":
    criar_tabelas()
    popular_categorias_padrao()
    print(f"Banco de dados criado em: {DB_PATH}")
