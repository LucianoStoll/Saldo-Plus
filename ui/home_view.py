"""
ui/home_view.py
Tela principal do Saldo+: monta o layout (hero card, formulário em
bottom sheet, lista de transações, navegação inferior), mantém o
estado da UI e conecta os eventos às funções de repository.py.

Esta é a função passada para ft.app(target=...) em app.py.
"""

from datetime import date

import flet as ft

import repository as repo
from ui import components as comp
from ui.theme import (
    COR_ACCENT,
    COR_BORDA,
    COR_DESPESA,
    COR_FUNDO,
    COR_SUPERFICIE,
    COR_SUPERFICIE_ALTA,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_CORPO,
    FONTE_DISPLAY,
    FONTES,
    estilo_campo,
    estilo_dropdown,
)


def build(page: ft.Page) -> None:
    """Constrói e conecta toda a tela principal na `page` recebida."""

    # -------------------------------------------------------------
    # Configuração da página
    # -------------------------------------------------------------
    page.title = "Saldo+"
    page.window.width = 390
    page.window.height = 844
    page.window.min_width = 360
    page.window.min_height = 640
    page.window.bgcolor = COR_FUNDO
    page.bgcolor = COR_FUNDO
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = FONTES
    page.theme = ft.Theme(font_family=FONTE_CORPO)
    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

    # -------------------------------------------------------------
    # Estado da tela
    # -------------------------------------------------------------
    tipo_selecionado = {"valor": "despesa"}

    # -------------------------------------------------------------
    # Controles com estado (precisam ser atualizados dinamicamente)
    # -------------------------------------------------------------
    saldo_valor_text = ft.Text(size=32, weight=ft.FontWeight.W_700, font_family=FONTE_DISPLAY, color=COR_TEXTO)
    receitas_mes_text = ft.Text(size=13, weight=ft.FontWeight.W_700, color="#1B2E12")
    despesas_mes_text = ft.Text(size=13, weight=ft.FontWeight.W_700, color=COR_DESPESA)
    lista_transacoes = ft.ListView(expand=True, spacing=6, auto_scroll=False)
    tipo_row = ft.Row(spacing=10)

    conta_dropdown = ft.Dropdown(label="Conta", expand=True, **estilo_dropdown())
    categoria_dropdown = ft.Dropdown(label="Categoria", expand=True, **estilo_dropdown())
    valor_field = ft.TextField(
        label="Valor (R$)", expand=True, keyboard_type=ft.KeyboardType.NUMBER,
        prefix=ft.Text("R$ ", color=COR_TEXTO_SUAVE), **estilo_campo(),
    )
    descricao_field = ft.TextField(label="Descrição", expand=True, **estilo_campo())
    data_field = ft.TextField(label="Data (AAAA-MM-DD)", value=str(date.today()), expand=True, **estilo_campo())

    nova_conta_nome = ft.TextField(label="Nome da conta", expand=True, **estilo_campo())
    nova_conta_saldo = ft.TextField(label="Saldo inicial", value="0", expand=True, keyboard_type=ft.KeyboardType.NUMBER, **estilo_campo())

    # -------------------------------------------------------------
    # Toggle de tipo (receita / despesa)
    # -------------------------------------------------------------
    def montar_tipo_row():
        tipo_row.controls = [
            comp.pilula_tipo("Despesa", "despesa", tipo_selecionado["valor"] == "despesa", selecionar_tipo),
            comp.pilula_tipo("Receita", "receita", tipo_selecionado["valor"] == "receita", selecionar_tipo),
        ]

    def selecionar_tipo(valor: str):
        tipo_selecionado["valor"] = valor
        montar_tipo_row()
        atualizar_dropdown_categorias()
        page.update()

    # -------------------------------------------------------------
    # Sincronização com o banco de dados
    # -------------------------------------------------------------
    def atualizar_dropdown_contas():
        contas = repo.listar_contas()
        conta_dropdown.options = [ft.dropdown.Option(str(c.id), c.nome) for c in contas]
        if contas and not conta_dropdown.value:
            conta_dropdown.value = str(contas[0].id)

    def atualizar_dropdown_categorias():
        categorias = repo.listar_categorias(tipo=tipo_selecionado["valor"])
        categoria_dropdown.options = [ft.dropdown.Option(str(c.id), c.nome) for c in categorias]
        categoria_dropdown.value = str(categorias[0].id) if categorias else None

    def atualizar_saldo():
        total = repo.saldo_total()
        saldo_valor_text.value = f"R$ {total:,.2f}"

        resumo = repo.resumo_mes()
        receitas_mes_text.value = f"+R$ {resumo['receitas']:,.2f}"
        despesas_mes_text.value = f"−R$ {resumo['despesas']:,.2f}"

    def atualizar_lista_transacoes():
        transacoes = repo.listar_transacoes()
        lista_transacoes.controls.clear()
        if not transacoes:
            lista_transacoes.controls.append(
                comp.estado_vazio("Nenhuma transação ainda", "Toque no + para adicionar.")
            )
        else:
            for t in transacoes:
                lista_transacoes.controls.append(comp.linha_transacao(t, on_click=confirmar_exclusao))

    def atualizar_tudo():
        atualizar_dropdown_contas()
        atualizar_dropdown_categorias()
        atualizar_saldo()
        atualizar_lista_transacoes()
        page.update()

    # -------------------------------------------------------------
    # Handlers de eventos
    # -------------------------------------------------------------
    def adicionar_transacao(e):
        if not conta_dropdown.value or not categoria_dropdown.value or not valor_field.value:
            page.show_dialog(ft.SnackBar(ft.Text("Preencha conta, categoria e valor.")))
            return
        try:
            valor = float(valor_field.value.replace(",", "."))
        except ValueError:
            page.show_dialog(ft.SnackBar(ft.Text("Valor inválido.")))
            return

        repo.criar_transacao(
            conta_id=int(conta_dropdown.value),
            categoria_id=int(categoria_dropdown.value),
            valor=valor,
            data=data_field.value or str(date.today()),
            descricao=descricao_field.value,
            tipo=tipo_selecionado["valor"],
        )

        valor_field.value = ""
        descricao_field.value = ""
        page.pop_dialog()
        atualizar_tudo()

    def confirmar_exclusao(transacao_id: int):
        def excluir():
            repo.excluir_transacao(transacao_id)
            page.pop_dialog()
            atualizar_tudo()

        page.show_dialog(
            comp.dialogo_confirmacao(
                titulo="Excluir transação?",
                mensagem="Essa ação não pode ser desfeita.",
                on_confirmar=excluir,
                on_cancelar=page.pop_dialog,
            )
        )

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
        page.pop_dialog()
        atualizar_tudo()

    def abrir_dialogo_conta(e):
        page.pop_dialog()
        page.show_dialog(dialogo_nova_conta)

    def abrir_form_transacao(e):
        page.show_dialog(bottom_sheet)

    # -------------------------------------------------------------
    # Diálogo: nova conta
    # -------------------------------------------------------------
    dialogo_nova_conta = ft.AlertDialog(
        modal=True,
        bgcolor=COR_SUPERFICIE_ALTA,
        title=ft.Text("Nova conta", font_family=FONTE_DISPLAY, color=COR_TEXTO),
        content=ft.Column([nova_conta_nome, nova_conta_saldo], tight=True, height=140),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog(), style=ft.ButtonStyle(color=COR_TEXTO_SUAVE)),
            ft.FilledButton("Salvar", on_click=adicionar_conta, style=ft.ButtonStyle(bgcolor=COR_ACCENT, color=COR_FUNDO)),
        ],
    )

    # -------------------------------------------------------------
    # Bottom sheet: nova transação
    # -------------------------------------------------------------
    montar_tipo_row()

    formulario_sheet = ft.Container(
        content=ft.Column(
            [
                ft.Row([ft.Container(width=36, height=4, bgcolor=COR_BORDA, border_radius=2)],
                       alignment=ft.MainAxisAlignment.CENTER),
                ft.Text("Nova transação", size=18, weight=ft.FontWeight.W_700, font_family=FONTE_DISPLAY, color=COR_TEXTO),
                tipo_row,
                ft.Row([conta_dropdown, ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_color=COR_ACCENT, tooltip="Nova conta", on_click=abrir_dialogo_conta)]),
                categoria_dropdown,
                ft.Row([valor_field, data_field]),
                descricao_field,
                ft.FilledButton(
                    "Adicionar transação",
                    icon=ft.Icons.ADD_ROUNDED,
                    on_click=adicionar_transacao,
                    style=ft.ButtonStyle(bgcolor=COR_ACCENT, color=COR_FUNDO, shape=ft.RoundedRectangleBorder(radius=12)),
                    height=48,
                ),
            ],
            spacing=14,
            tight=True,
        ),
        bgcolor=COR_SUPERFICIE,
        padding=ft.Padding.only(left=20, right=20, top=14, bottom=24),
        border_radius=ft.BorderRadius.only(top_left=24, top_right=24),
    )

    bottom_sheet = ft.BottomSheet(
        content=formulario_sheet,
        bgcolor=COR_SUPERFICIE,
        show_drag_handle=False,
        scrollable=True,
        use_safe_area=True,
    )

    # -------------------------------------------------------------
    # Cabeçalho
    # -------------------------------------------------------------
    cabecalho = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Olá 👋", size=12, color=COR_TEXTO_SUAVE),
                        ft.Text("Saldo+", size=22, weight=ft.FontWeight.W_800, font_family=FONTE_DISPLAY, color=COR_TEXTO),
                    ],
                    spacing=0,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.SAVINGS_ROUNDED, color=COR_FUNDO, size=20),
                    bgcolor=COR_ACCENT,
                    border_radius=12,
                    padding=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.Padding.only(left=20, right=20, top=20, bottom=16),
    )

    # -------------------------------------------------------------
    # Corpo (coluna única rolável)
    # -------------------------------------------------------------
    corpo = ft.Container(
        content=ft.Column(
            [
                comp.hero_saldo_card(saldo_valor_text, receitas_mes_text, despesas_mes_text),
                ft.Container(
                    content=ft.Text("Transações recentes", size=15, weight=ft.FontWeight.W_700, font_family=FONTE_DISPLAY, color=COR_TEXTO),
                    padding=ft.Padding.only(left=20, right=20, top=8, bottom=4),
                ),
                ft.Container(
                    content=lista_transacoes,
                    padding=ft.Padding.only(left=20, right=20, bottom=90),
                    expand=True,
                ),
            ],
            spacing=14,
            expand=True,
        ),
        expand=True,
    )

    # -------------------------------------------------------------
    # Navegação inferior + FAB
    # -------------------------------------------------------------
    page.navigation_bar = ft.NavigationBar(
        bgcolor=COR_SUPERFICIE,
        indicator_color=COR_ACCENT,
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_ROUNDED, label="Início"),
            ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART_OUTLINE_ROUNDED, label="Resumo"),
            ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE_OUTLINED, label="Contas"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, label="Ajustes"),
        ],
    )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED,
        bgcolor=COR_ACCENT,
        foreground_color=COR_FUNDO,
        shape=ft.CircleBorder(),
        on_click=abrir_form_transacao,
    )

    # -------------------------------------------------------------
    # Monta a página e carrega os dados iniciais
    # -------------------------------------------------------------
    page.add(cabecalho, corpo)
    atualizar_tudo()
