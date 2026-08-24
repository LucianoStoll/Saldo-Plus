"""
ui/theme.py
Identidade visual do Saldo+ (dark, verde neon) e pequenos helpers
de formatação/ícone usados pelos componentes e pela tela principal.
Nenhuma lógica de estado ou de aplicativo mora aqui — só constantes
e funções puras, para poder mudar o visual do app inteiro num só lugar.
"""

import flet as ft

# ---------------------------------------------------------------------------
# Cores
# ---------------------------------------------------------------------------
COR_FUNDO = "#0A0E14"
COR_SUPERFICIE = "#141A22"
COR_SUPERFICIE_ALTA = "#1B222C"
COR_BORDA = "#262E38"
COR_TEXTO = "#F4F6F8"
COR_TEXTO_SUAVE = "#8B93A1"
COR_ACCENT = "#C6F135"
COR_RECEITA = "#C6F135"
COR_RECEITA_FUNDO = "#1E2A12"
COR_DESPESA = "#FF6B6B"
COR_DESPESA_FUNDO = "#2E1618"

# ---------------------------------------------------------------------------
# Fontes
# ---------------------------------------------------------------------------
FONTE_DISPLAY = "Manrope"
FONTE_CORPO = "Inter"

FONTES = {
    "Manrope": "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf",
    "Inter": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
}

# ---------------------------------------------------------------------------
# Ícones por categoria
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Estilos padrão de campos de formulário
# ---------------------------------------------------------------------------
def estilo_campo() -> dict:
    return dict(
        border_color=COR_BORDA,
        border_radius=12,
        bgcolor=COR_SUPERFICIE_ALTA,
        color=COR_TEXTO,
        label_style=ft.TextStyle(color=COR_TEXTO_SUAVE),
        cursor_color=COR_ACCENT,
        focused_border_color=COR_ACCENT,
    )


def estilo_dropdown() -> dict:
    return dict(
        border_color=COR_BORDA,
        border_radius=12,
        bgcolor=COR_SUPERFICIE_ALTA,
        color=COR_TEXTO,
        label_style=ft.TextStyle(color=COR_TEXTO_SUAVE),
        focused_border_color=COR_ACCENT,
    )
