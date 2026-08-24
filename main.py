"""
main.py
Interface gráfica (Flet) do Saldo+ — tema dark com acento verde neon,
inspirado em referência visual de apps fintech (hero card em gradiente,
cartões escuros arredondados).
Execute com: python main.py
"""

import flet as ft
from datetime import date

from database import criar_tabelas, popular_categorias_padrao
import repository as repo

# ---------------------------------------------------------------------------
# Identidade visual — dark fintech
# ---------------------------------------------------------------------------
COR_FUNDO = "#0A0E14"
COR_SUPERFICIE = "#141A22"
COR_SUPERFICIE_ALTA = "#1B222C"
COR_BORDA = "#262E38"
COR_TEXTO = "#F4F6F8"
COR_TEXTO_SUAVE = "#8B93A1"
COR_ACCENT = "#C6F135"        # verde neon (assinatura do app)
COR_ACCENT_ESCURO = "#1B2E12"  # verde neon escurecido p/ fundo de ícone
COR_RECEITA = "#C6F135"
COR_RECEITA_FUNDO = "#1E2A12"
COR_DESPESA = "#FF6B6B"
COR_DESPESA_FUNDO = "#2E1618"

FONTE_DISPLAY = "Manrope"
FONTE_CORPO = "Inter"

ICONES_CATEGORIA = {
    "salário": ft.Icons.WORK_OUTLINE,
    "outras receitas": ft.Icons.PAID_OUTLINED,
    "alimentação": ft.Icons.RESTAURANT_OUTLINED,
    "transporte": ft.Icons.DIRECTIONS_CAR_OUTLINED,
    "moradia": ft.Icons.HOME_OUTLINED,
    "lazer": ft.Icons.SPORTS_ESPORTS_OUTLINED,
    "saúde": ft.Icons.LOCAL_HOSPITAL_OUTLINED,
    "outras despesas": ft.Icons.RECEIPT_LONG_OUTLINED,
}


def icone_categoria(nome: str) -> str:
    return ICONES_CATEGORIA.get(nome.lower(), ft.Icons.LABEL_OUTLINE)


def formatar_data_br(data_iso: str) -> str:
    try:
        y, m, d = data_iso.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return data_iso


def main(page: ft.Page):
    page.title = "Saldo+"
    page.window.width = 1060
    page.window.height = 740
    page.window.min_width = 780
    page.window.min_height = 580
    page.window.bgcolor = COR_FUNDO
    page.bgcolor = COR_FUNDO
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = {
        "Manrope": "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf",
        "Inter": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    }
    page.theme = ft.Theme(font_family=FONTE_CORPO)

    # -----------------------------------------------------------------
    # Estado / referências de UI
    # -----------------------------------------------------------------
    tipo_selecionado = {"valor": "despesa"}

    saldo_valor_text = ft.Text(size=36, weight=ft.FontWeight.W_700, font_family=FONTE_DISPLAY, color=COR_TEXTO)
    receitas_mes_text = ft.Text(size=19, weight=ft.FontWeight.W_700, color=COR_RECEITA)
    despesas_mes_text = ft.Text(size=19, weight=ft.FontWeight.W_700, color=COR_DESPESA)

    lista_transacoes = ft.ListView(expand=True, spacing=6, auto_scroll=False)

    def estilo_campo():
        return dict(
            border_color=COR_BORDA,
            border_radius=12,
            bgcolor=COR_SUPERFICIE_ALTA,
            color=COR_TEXTO,
            label_style=ft.TextStyle(color=COR_TEXTO_SUAVE),
            cursor_color=COR_ACCENT,
            focused_border_color=COR_ACCENT,
        )

    def estilo_dropdown():
        return dict(
            border_color=COR_BORDA,
            border_radius=12,
            bgcolor=COR_SUPERFICIE_ALTA,
            color=COR_TEXTO,
            label_style=ft.TextStyle(color=COR_TEXTO_SUAVE),
            focused_border_color=COR_ACCENT,
        )

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

    # -----------------------------------------------------------------
    # Toggle de tipo (receita / despesa) — pílulas
    # -----------------------------------------------------------------
    def pilula_tipo(label: str, valor: str):
        selecionada = tipo_selecionado["valor"] == valor
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
            on_click=lambda e, v=valor: selecionar_tipo(v),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

    tipo_row = ft.Row(spacing=10)

    def montar_tipo_row():
        tipo_row.controls = [
            pilula_tipo("Despesa", "despesa"),
            pilula_tipo("Receita", "receita"),
        ]

    def selecionar_tipo(valor: str):
        tipo_selecionado["valor"] = valor
        montar_tipo_row()
        atualizar_dropdown_categorias()
        page.update()

    # -----------------------------------------------------------------
    # Funções auxiliares
    # -----------------------------------------------------------------
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

    def linha_transacao(t: dict) -> ft.Control:
        is_receita = t["tipo"] == "receita"
        cor = COR_RECEITA if is_receita else COR_DESPESA
        cor_fundo = COR_RECEITA_FUNDO if is_receita else COR_DESPESA_FUNDO
        sinal = "+" if is_receita else "−"

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icone_categoria(t["categoria_nome"]), color=cor, size=18),
                        bgcolor=cor_fundo,
                        border_radius=10,
                        padding=10,
                    ),
                    ft.Column(
                        [
                            ft.Text(t["descricao"] or t["categoria_nome"], weight=ft.FontWeight.W_600, size=14, color=COR_TEXTO),
                            ft.Text(
                                f"{t['categoria_nome']}  ·  {t['conta_nome']}  ·  {formatar_data_br(t['data'])}",
                                size=12,
                                color=COR_TEXTO_SUAVE,
                            ),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.Text(f"{sinal} R$ {t['valor']:,.2f}", color=cor, weight=ft.FontWeight.W_700, size=14),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE_ROUNDED,
                        icon_color=COR_TEXTO_SUAVE,
                        icon_size=16,
                        on_click=lambda e, tid=t["id"]: excluir_transacao(tid),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COR_SUPERFICIE,
            border=ft.Border.all(1, COR_BORDA),
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )

    def atualizar_lista_transacoes():
        transacoes = repo.listar_transacoes()
        lista_transacoes.controls.clear()
        if not transacoes:
            lista_transacoes.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SAVINGS_OUTLINED, size=36, color=COR_TEXTO_SUAVE),
                            ft.Text("Nenhuma transação ainda", color=COR_TEXTO_SUAVE, size=14),
                            ft.Text("Adicione a primeira ao lado.", color=COR_TEXTO_SUAVE, size=12),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=40,
                )
            )
        else:
            for t in transacoes:
                lista_transacoes.controls.append(linha_transacao(t))

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
        page.pop_dialog()
        atualizar_tudo()

    def abrir_dialogo_conta(e):
        page.show_dialog(dialogo_nova_conta)

    def fechar_dialogo_conta(e):
        page.pop_dialog()

    # -----------------------------------------------------------------
    # Diálogo para criar nova conta
    # -----------------------------------------------------------------
    dialogo_nova_conta = ft.AlertDialog(
        modal=True,
        bgcolor=COR_SUPERFICIE_ALTA,
        title=ft.Text("Nova conta", font_family=FONTE_DISPLAY, color=COR_TEXTO),
        content=ft.Column([nova_conta_nome, nova_conta_saldo], tight=True, height=140),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_dialogo_conta, style=ft.ButtonStyle(color=COR_TEXTO_SUAVE)),
            ft.FilledButton(
                "Salvar", on_click=adicionar_conta,
                style=ft.ButtonStyle(bgcolor=COR_ACCENT, color=COR_FUNDO),
            ),
        ],
    )

    # -----------------------------------------------------------------
    # Hero card — saldo total, em gradiente (referência visual)
    # -----------------------------------------------------------------
    hero_saldo = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Saldo total", size=13, color="#E9FFB0", weight=ft.FontWeight.W_600),
                        ft.Container(
                            content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, size=16, color=COR_FUNDO),
                            bgcolor="#00000022",
                            border_radius=8,
                            padding=6,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                saldo_valor_text,
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.TRENDING_UP_ROUNDED, size=14, color="#0A0E14"),
                                ft.Text("Receitas", size=12, color="#1B2E12", weight=ft.FontWeight.W_600),
                                receitas_mes_text,
                            ],
                            spacing=4,
                        ),
                    ],
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
        padding=22,
        expand=2,
    )

    def card_resumo(titulo: str, valor_control: ft.Text, icone: str, cor: str, cor_fundo: str):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(ft.Icon(icone, color=cor, size=18), bgcolor=cor_fundo, border_radius=8, padding=8),
                            ft.Text(titulo, size=13, color=COR_TEXTO_SUAVE, weight=ft.FontWeight.W_500),
                        ],
                        spacing=8,
                    ),
                    valor_control,
                ],
                spacing=14,
            ),
            bgcolor=COR_SUPERFICIE,
            border=ft.Border.all(1, COR_BORDA),
            border_radius=20,
            padding=22,
            expand=1,
        )

    cards_resumo = ft.Row(
        [
            hero_saldo,
            card_resumo("Despesas do mês", despesas_mes_text, ft.Icons.TRENDING_DOWN_ROUNDED, COR_DESPESA, COR_DESPESA_FUNDO),
        ],
        spacing=14,
    )

    # -----------------------------------------------------------------
    # Formulário
    # -----------------------------------------------------------------
    montar_tipo_row()

    formulario = ft.Container(
        content=ft.Column(
            [
                ft.Text("Nova transação", size=17, weight=ft.FontWeight.W_700, font_family=FONTE_DISPLAY, color=COR_TEXTO),
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
                    height=46,
                ),
            ],
            spacing=14,
        ),
        bgcolor=COR_SUPERFICIE,
        border=ft.Border.all(1, COR_BORDA),
        border_radius=20,
        padding=20,
        width=360,
    )

    # -----------------------------------------------------------------
    # Layout geral
    # -----------------------------------------------------------------
    cabecalho = ft.Container(
        content=ft.Row(
            [
                ft.Container(ft.Icon(ft.Icons.SAVINGS_ROUNDED, color=COR_FUNDO, size=22), bgcolor=COR_ACCENT, border_radius=12, padding=10),
                ft.Column(
                    [
                        ft.Text("Saldo+", size=24, weight=ft.FontWeight.W_800, font_family=FONTE_DISPLAY, color=COR_TEXTO),
                        ft.Text("seu controle de finanças pessoais", size=12, color=COR_TEXTO_SUAVE),
                    ],
                    spacing=0,
                ),
            ],
            spacing=12,
        ),
        padding=ft.Padding.only(left=28, right=28, top=24, bottom=8),
    )

    corpo = ft.Container(
        content=ft.Column(
            [
                cards_resumo,
                ft.Row(
                    [
                        formulario,
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Transações", size=17, weight=ft.FontWeight.W_700, font_family=FONTE_DISPLAY, color=COR_TEXTO),
                                    lista_transacoes,
                                ],
                                expand=True,
                                spacing=12,
                            ),
                            expand=True,
                        ),
                    ],
                    expand=True,
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=20,
            expand=True,
        ),
        padding=ft.Padding.only(left=28, right=28, bottom=24),
        expand=True,
    )

    page.add(cabecalho, corpo)
    atualizar_tudo()


if __name__ == "__main__":
    criar_tabelas()
    popular_categorias_padrao()
    ft.app(target=main)