"""
main.py
Interface gráfica (Flet) do Controle de Finanças.
Execute com: flet run main.py  (ou: python main.py)
"""

import flet as ft
from datetime import date

from database import criar_tabelas, popular_categorias_padrao
import repository as repo


def main(page: ft.Page):
    page.title = "Controle de Finanças"
    page.window.width = 900
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # -----------------------------------------------------------------
    # Estado / referências de UI
    # -----------------------------------------------------------------
    saldo_text = ft.Text(size=28, weight=ft.FontWeight.BOLD)
    lista_transacoes = ft.ListView(expand=True, spacing=8, auto_scroll=False)

    conta_dropdown = ft.Dropdown(label="Conta", expand=True)
    categoria_dropdown = ft.Dropdown(label="Categoria", expand=True)
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[ft.dropdown.Option("receita"), ft.dropdown.Option("despesa")],
        value="despesa",
        expand=True,
    )
    valor_field = ft.TextField(label="Valor (R$)", expand=True, keyboard_type=ft.KeyboardType.NUMBER)
    descricao_field = ft.TextField(label="Descrição", expand=True)
    data_field = ft.TextField(label="Data (AAAA-MM-DD)", value=str(date.today()), expand=True)

    nova_conta_nome = ft.TextField(label="Nome da conta", expand=True)
    nova_conta_saldo = ft.TextField(label="Saldo inicial", value="0", expand=True, keyboard_type=ft.KeyboardType.NUMBER)

    # -----------------------------------------------------------------
    # Funções auxiliares
    # -----------------------------------------------------------------
    def atualizar_dropdown_contas():
        contas = repo.listar_contas()
        conta_dropdown.options = [ft.dropdown.Option(str(c.id), c.nome) for c in contas]
        if contas and not conta_dropdown.value:
            conta_dropdown.value = str(contas[0].id)

    def atualizar_dropdown_categorias():
        categorias = repo.listar_categorias()
        categoria_dropdown.options = [
            ft.dropdown.Option(str(c.id), f"{c.nome} ({c.tipo})") for c in categorias
        ]

    def atualizar_saldo():
        total = repo.saldo_total()
        cor = ft.Colors.GREEN_700 if total >= 0 else ft.Colors.RED_700
        saldo_text.value = f"Saldo total: R$ {total:,.2f}"
        saldo_text.color = cor

    def atualizar_lista_transacoes():
        lista_transacoes.controls.clear()
        for t in repo.listar_transacoes():
            cor = ft.Colors.GREEN_700 if t["tipo"] == "receita" else ft.Colors.RED_700
            sinal = "+" if t["tipo"] == "receita" else "-"
            lista_transacoes.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(t["descricao"] or "(sem descrição)", weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{t['categoria_nome']} • {t['conta_nome']} • {t['data']}", size=12, color=ft.Colors.GREY_700),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.Text(f"{sinal} R$ {t['valor']:,.2f}", color=cor, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.GREY_500,
                                on_click=lambda e, tid=t["id"]: excluir_transacao(tid),
                            ),
                        ]
                    ),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                )
            )
        page.update()

    def atualizar_tudo():
        atualizar_dropdown_contas()
        atualizar_dropdown_categorias()
        atualizar_saldo()
        atualizar_lista_transacoes()
        page.update()

    # -----------------------------------------------------------------
    # Handlers
    # -----------------------------------------------------------------
    def adicionar_transacao(e):
        if not conta_dropdown.value or not categoria_dropdown.value or not valor_field.value:
            page.open(ft.SnackBar(ft.Text("Preencha conta, categoria e valor.")))
            return
        try:
            valor = float(valor_field.value.replace(",", "."))
        except ValueError:
            page.open(ft.SnackBar(ft.Text("Valor inválido.")))
            return

        repo.criar_transacao(
            conta_id=int(conta_dropdown.value),
            categoria_id=int(categoria_dropdown.value),
            valor=valor,
            data=data_field.value or str(date.today()),
            descricao=descricao_field.value,
            tipo=tipo_dropdown.value,
        )

        valor_field.value = ""
        descricao_field.value = ""
        atualizar_tudo()

    def excluir_transacao(transacao_id: int):
        repo.excluir_transacao(transacao_id)
        atualizar_tudo()

    def adicionar_conta(e):
        if not nova_conta_nome.value:
            return
        try:
            saldo = float(nova_conta_saldo.value.replace(",", "."))
        except ValueError:
            saldo = 0.0
        repo.criar_conta(nome=nova_conta_nome.value, tipo="corrente", saldo_inicial=saldo)
        nova_conta_nome.value = ""
        nova_conta_saldo.value = "0"
        fechar_dialogo_conta(e)
        atualizar_tudo()

    def abrir_dialogo_conta(e):
        page.open(dialogo_nova_conta)

    def fechar_dialogo_conta(e):
        page.close(dialogo_nova_conta)

    # -----------------------------------------------------------------
    # Diálogo para criar nova conta
    # -----------------------------------------------------------------
    dialogo_nova_conta = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nova conta"),
        content=ft.Column([nova_conta_nome, nova_conta_saldo], tight=True, height=140),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_dialogo_conta),
            ft.FilledButton("Salvar", on_click=adicionar_conta),
        ],
    )

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------
    formulario = ft.Container(
        content=ft.Column(
            [
                ft.Text("Nova transação", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([conta_dropdown, ft.IconButton(icon=ft.Icons.ADD, tooltip="Nova conta", on_click=abrir_dialogo_conta)]),
                ft.Row([categoria_dropdown, tipo_dropdown]),
                ft.Row([valor_field, data_field]),
                descricao_field,
                ft.FilledButton("Adicionar transação", icon=ft.Icons.ADD_CIRCLE, on_click=adicionar_transacao),
            ],
            spacing=12,
        ),
        padding=15,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
    )

    page.add(
        ft.Row([ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=32), ft.Text("Controle de Finanças", size=26, weight=ft.FontWeight.BOLD)]),
        saldo_text,
        ft.Row(
            [
                ft.Container(formulario, width=380),
                ft.Container(
                    content=ft.Column(
                        [ft.Text("Transações", size=18, weight=ft.FontWeight.BOLD), lista_transacoes],
                        expand=True,
                    ),
                    expand=True,
                    padding=15,
                ),
            ],
            expand=True,
        ),
    )

    atualizar_tudo()


if __name__ == "__main__":
    criar_tabelas()
    popular_categorias_padrao()
    ft.app(target=main)
