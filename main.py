"""
app.py
Ponto de entrada do Saldo+.

Só faz duas coisas: garante que o banco de dados existe (com as
categorias padrão) e sobe a aplicação Flet apontando para a tela
principal definida em ui/home_view.py.

Execute com: python app.py
"""

import flet as ft

from database import criar_tabelas, popular_categorias_padrao
from ui.home_view import build


def main():
    criar_tabelas()
    popular_categorias_padrao()
    ft.app(target=build)


if __name__ == "__main__":
    main()
