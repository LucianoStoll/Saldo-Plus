"""
repository.py
Camada de acesso a dados: funções que executam as operações
de CRUD no banco SQLite para contas, categorias e transações.
"""

from typing import List, Optional
from database import get_connection
from models import Conta, Categoria, Transacao


# ---------------------------------------------------------------------------
# CONTAS
# ---------------------------------------------------------------------------

def criar_conta(nome: str, tipo: str, saldo_inicial: float = 0.0) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contas (nome, tipo, saldo_inicial) VALUES (?, ?, ?)",
        (nome, tipo, saldo_inicial),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def listar_contas() -> List[Conta]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contas ORDER BY nome")
    linhas = cursor.fetchall()
    conn.close()
    return [Conta(**dict(l)) for l in linhas]


def excluir_conta(conta_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# CATEGORIAS
# ---------------------------------------------------------------------------

def criar_categoria(nome: str, tipo: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categorias (nome, tipo) VALUES (?, ?)",
        (nome, tipo),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def listar_categorias(tipo: Optional[str] = None) -> List[Categoria]:
    conn = get_connection()
    cursor = conn.cursor()
    if tipo:
        cursor.execute("SELECT * FROM categorias WHERE tipo = ? ORDER BY nome", (tipo,))
    else:
        cursor.execute("SELECT * FROM categorias ORDER BY tipo, nome")
    linhas = cursor.fetchall()
    conn.close()
    return [Categoria(**dict(l)) for l in linhas]


# ---------------------------------------------------------------------------
# TRANSAÇÕES
# ---------------------------------------------------------------------------

def criar_transacao(conta_id: int, categoria_id: int, valor: float,
                     data: str, descricao: str, tipo: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO transacoes (conta_id, categoria_id, valor, data, descricao, tipo)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (conta_id, categoria_id, valor, data, descricao, tipo),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def listar_transacoes(conta_id: Optional[int] = None) -> List[dict]:
    """Retorna transações já com nome da conta e da categoria (join)."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT t.id, t.valor, t.data, t.descricao, t.tipo,
               c.nome AS conta_nome, cat.nome AS categoria_nome
        FROM transacoes t
        JOIN contas c ON c.id = t.conta_id
        JOIN categorias cat ON cat.id = t.categoria_id
    """
    params = ()
    if conta_id:
        query += " WHERE t.conta_id = ?"
        params = (conta_id,)
    query += " ORDER BY t.data DESC, t.id DESC"

    cursor.execute(query, params)
    linhas = cursor.fetchall()
    conn.close()
    return [dict(l) for l in linhas]


def excluir_transacao(transacao_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# SALDOS / RELATÓRIOS
# ---------------------------------------------------------------------------

def saldo_da_conta(conta_id: int) -> float:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT saldo_inicial FROM contas WHERE id = ?", (conta_id,))
    linha = cursor.fetchone()
    saldo = linha["saldo_inicial"] if linha else 0.0

    cursor.execute(
        """SELECT
             COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) AS receitas,
             COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0) AS despesas
           FROM transacoes WHERE conta_id = ?""",
        (conta_id,),
    )
    r = cursor.fetchone()
    saldo += r["receitas"] - r["despesas"]

    conn.close()
    return saldo


def saldo_total() -> float:
    contas = listar_contas()
    return sum(saldo_da_conta(c.id) for c in contas)


def resumo_mes(ano_mes: Optional[str] = None) -> dict:
    """Total de receitas e despesas de um mês (formato 'AAAA-MM'). Usa o mês atual se None."""
    from datetime import date as _date
    ano_mes = ano_mes or _date.today().strftime("%Y-%m")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT
             COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) AS receitas,
             COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0) AS despesas
           FROM transacoes WHERE substr(data, 1, 7) = ?""",
        (ano_mes,),
    )
    r = cursor.fetchone()
    conn.close()
    return {"receitas": r["receitas"], "despesas": r["despesas"]}


def resumo_por_categoria() -> List[dict]:
    """Total gasto/recebido por categoria (útil para gráficos)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cat.nome AS categoria, cat.tipo, SUM(t.valor) AS total
        FROM transacoes t
        JOIN categorias cat ON cat.id = t.categoria_id
        GROUP BY cat.id
        ORDER BY total DESC
    """)
    linhas = cursor.fetchall()
    conn.close()
    return [dict(l) for l in linhas]
