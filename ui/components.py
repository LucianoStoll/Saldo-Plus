"""
ui/components.py
Peças de interface reutilizáveis do Saldo+. Cada função recebe os
dados/callbacks que precisa e devolve um Control do Flet — sem
depender de estado global nem de repository.py. Isso deixa os
componentes fáceis de testar e de reaproveitar em outras telas.
"""

from typing import Callable, Optional

import flet as ft

from ui.theme import (
    COR_ACCENT,
    COR_BORDA,
    COR_DESPESA,
    COR_DESPESA_FUNDO,
    COR_FUNDO,
    COR_RECEITA,
    COR_RECEITA_FUNDO,
    COR_SUPERFICIE,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_DISPLAY,
    formatar_data_br,
    icone_categoria,
)


def pilula_tipo(label: str, valor: str, selecionada: bool, on_click: Callable) -> ft.Container:
    """Pílula de seleção usada no toggle Receita/Despesa."""
    return ft.Container(
        content=ft.Text(
            label,
            color=COR_FUNDO if selecionada else COR_TEXTO_SUAVE,
            weight=ft.FontWeight.W_700 if selecionada else ft.FontWeight.NORMAL,
            size=13,
        ),
        bgcolor=COR_ACCENT if selecionada else "transparent",
        border=ft.Border.all(1.5, COR_ACCENT if selecionada else COR_BORDA),
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        on_click=lambda e: on_click(valor),
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
    )


def hero_saldo_card(saldo_text: ft.Text, receitas_text: ft.Text, despesas_text: ft.Text) -> ft.Container:
    """Card em destaque (gradiente) com o saldo total e o resumo do mês."""
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Saldo total", size=13, color="#E9FFB0", weight=ft.FontWeight.W_600),
                        ft.Container(
                            content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE_ROUNDED, size=16, color=COR_FUNDO),
                            bgcolor="#00000022",
                            border_radius=8,
                            padding=6,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                saldo_text,
                ft.Row(
                    [
                        ft.Row([ft.Icon(ft.Icons.TRENDING_UP_ROUNDED, size=13, color="#1B2E12"), receitas_text], spacing=4),
                        ft.Row([ft.Icon(ft.Icons.TRENDING_DOWN_ROUNDED, size=13, color=COR_DESPESA), despesas_text], spacing=4),
                    ],
                    spacing=16,
                ),
            ],
            spacing=10,
        ),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#0F1710", COR_ACCENT],
        ),
        border_radius=20,
        padding=20,
        margin=ft.Margin.symmetric(horizontal=20),
    )


def linha_transacao(t: dict, on_click: Optional[Callable] = None) -> ft.Container:
    """Um item da lista de transações."""
    is_receita = t["tipo"] == "receita"
    cor = COR_RECEITA if is_receita else COR_DESPESA
    cor_fundo = COR_RECEITA_FUNDO if is_receita else COR_DESPESA_FUNDO
    sinal = "+" if is_receita else "−"

    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icone_categoria(t["categoria_nome"]), color=cor, size=17),
                    bgcolor=cor_fundo,
                    border_radius=10,
                    padding=9,
                ),
                ft.Column(
                    [
                        ft.Text(t["descricao"] or t["categoria_nome"], weight=ft.FontWeight.W_600, size=13, color=COR_TEXTO),
                        ft.Text(
                            f"{t['categoria_nome']} · {formatar_data_br(t['data'])}",
                            size=11,
                            color=COR_TEXTO_SUAVE,
                        ),
                    ],
                    expand=True,
                    spacing=2,
                ),
                ft.Text(f"{sinal} {t['valor']:,.2f}", color=cor, weight=ft.FontWeight.W_700, size=13),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COR_SUPERFICIE,
        border=ft.Border.all(1, COR_BORDA),
        border_radius=14,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        on_click=(lambda e: on_click(t["id"])) if on_click else None,
    )


def estado_vazio(mensagem: str, dica: str) -> ft.Container:
    """Placeholder mostrado quando a lista de transações está vazia."""
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.SAVINGS_OUTLINED, size=32, color=COR_TEXTO_SUAVE),
                ft.Text(mensagem, color=COR_TEXTO_SUAVE, size=13),
                ft.Text(dica, color=COR_TEXTO_SUAVE, size=11),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        alignment=ft.Alignment.CENTER,
        padding=32,
    )


def dialogo_confirmacao(titulo: str, mensagem: str, on_confirmar: Callable, on_cancelar: Callable,
                         label_confirmar: str = "Excluir") -> ft.AlertDialog:
    """Diálogo genérico de confirmação (ex.: excluir transação)."""
    from ui.theme import COR_SUPERFICIE_ALTA
    return ft.AlertDialog(
        modal=True,
        bgcolor=COR_SUPERFICIE_ALTA,
        title=ft.Text(titulo, color=COR_TEXTO, font_family=FONTE_DISPLAY),
        content=ft.Text(mensagem, color=COR_TEXTO_SUAVE),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: on_cancelar(), style=ft.ButtonStyle(color=COR_TEXTO_SUAVE)),
            ft.TextButton(label_confirmar, on_click=lambda e: on_confirmar(), style=ft.ButtonStyle(color=COR_DESPESA)),
        ],
    )
