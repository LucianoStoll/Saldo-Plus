"""
models.py
Representações simples (dataclasses) das entidades do sistema.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Conta:
    id: Optional[int]
    nome: str
    tipo: str
    saldo_inicial: float


@dataclass
class Categoria:
    id: Optional[int]
    nome: str
    tipo: str  # 'receita' ou 'despesa'


@dataclass
class Subcategoria:
    id: Optional[int]
    categoria_id: int
    nome: str


@dataclass
class Transacao:
    id: Optional[int]
    conta_id: int
    categoria_id: int
    valor: float
    data: str  # formato ISO: YYYY-MM-DD
    descricao: str
    tipo: str  # 'receita' ou 'despesa'
    subcategoria_id: Optional[int] = None
