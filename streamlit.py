"""Cotar Moedas: conversor e cotações em tempo real (AwesomeAPI)."""
from __future__ import annotations

from datetime import datetime

import requests
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
API_URL = "https://economia.awesomeapi.com.br/json/last/{pares}"
CACHE_TTL = 30  # segundos
MAX_HISTORICO = 8

MOEDAS_ORIGEM = {
    "USD": "Dólar americano",
    "EUR": "Euro",
    "GBP": "Libra esterlina",
    "ARS": "Peso argentino",
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
}
DESTAQUES = ("USD-BRL", "EUR-BRL", "GBP-BRL", "BTC-BRL")

st.set_page_config(
    page_title="Cotar Moedas",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILO
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg: #1E2B3A;
    --surface: #28394C;
    --field: #1E2B3A;
    --border: #3D5166;
    --text: #F4F7FA;
    --muted: #C3D0DC;
    --accent: #3EE0B5;
    --up: #6CC4FF;
    --down: #FFAB70;
}

html, body, .stApp, [data-testid="stSidebar"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
.block-container { max-width: 1200px; padding-top: 2.5rem; padding-bottom: 4rem; }

/* Força texto claro em tudo, independente do tema do Streamlit */
.stApp, .stApp p, .stApp span, .stApp li, .stApp h1, .stApp h2, .stApp h3,
[data-testid="stSidebar"] *, [data-testid="stMarkdownContainer"] { color: var(--text); }
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"], .stCaption { color: var(--muted) !important; }

/* Limpa o chrome do Streamlit sem esconder o botão da barra lateral */
#MainMenu, footer, [data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }
header[data-testid="stHeader"] * { color: var(--text); }

/* Barra lateral */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }

/* Campos */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div {
    background: var(--field) !important; border-color: var(--border) !important; border-radius: 8px;
}
[data-baseweb="input"] input, [data-baseweb="select"] div, [data-baseweb="select"] span {
    color: var(--text) !important; -webkit-text-fill-color: var(--text);
}
[data-baseweb="select"] svg, [data-testid^="stNumberInputStep"] svg { fill: var(--text); color: var(--text); }
[data-testid^="stNumberInputStep"] { background: var(--field); color: var(--text); }
[data-baseweb="popover"] ul, [data-baseweb="popover"] li, [data-baseweb="menu"] {
    background: var(--surface) !important; color: var(--text) !important;
}
[data-baseweb="popover"] li:hover { background: var(--border) !important; }

/* Botões */
.stButton > button {
    background: transparent; color: var(--text); border: 1px solid var(--border); border-radius: 8px;
}
.stButton > button:hover { border-color: var(--accent); color: var(--accent); }

/* Títulos */
.page-title { font-size: 2.5rem; font-weight: 700; line-height: 1.2; margin: 0; }
.page-subtitle { color: var(--muted); font-size: 1.05rem; margin: .5rem 0 2.5rem; }
.section-title { font-size: 1.4rem; font-weight: 700; margin: 2.5rem 0 1rem; }

/* Conversor (container com key="conversor") */
.st-key-conversor {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.75rem;
}

/* Resultado */
.resultado { display: flex; flex-wrap: wrap; align-items: baseline; gap: 1rem 2rem;
             border-top: 1px solid var(--border); margin-top: 1.25rem; padding-top: 1.5rem; }
.resultado-rotulo { color: var(--muted); font-size: .9rem; }
.resultado-valor { font-family: 'DM Mono', monospace; font-size: 2.5rem; font-weight: 500; }
.resultado-taxa { color: var(--muted); font-size: .95rem; }
.resultado-taxa b { color: var(--text); font-family: 'DM Mono', monospace; font-weight: 500; }

/* Cards de cotação */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
        padding: 1.25rem 1.5rem; height: 100%; }
.card-titulo { color: var(--muted); font-size: .9rem; font-weight: 500; }
.card-valor { font-family: 'DM Mono', monospace; font-size: 1.75rem; font-weight: 500; margin: .35rem 0; }
.card-var { font-size: .9rem; font-weight: 700; }
.card-var.up { color: var(--up) !important; }
.card-var.down { color: var(--down) !important; }
.card-faixa { color: var(--muted); font-size: .8rem; margin-top: .75rem; padding-top: .75rem;
              border-top: 1px solid var(--border); font-family: 'DM Mono', monospace; }

/* Histórico */
.hist-item { display: flex; justify-content: space-between; align-items: baseline;
             padding: .6rem 0; border-bottom: 1px solid var(--border); font-size: .9rem; }
.hist-item span:first-child { font-weight: 500; }
.hist-hora { color: var(--muted) !important; font-size: .8rem; }
.hist-taxa { font-family: 'DM Mono', monospace; }
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# DADOS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def consultar_cotacoes(pares: tuple[str, ...]) -> dict:
    """Busca vários pares em uma única chamada. Retorna {} em caso de erro."""
    try:
        resposta = requests.get(API_URL.format(pares=",".join(pares)), timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except (requests.RequestException, ValueError):
        return {}


def chave_par(par: str) -> str:
    return par.replace("-", "")


# ─────────────────────────────────────────────────────────────────────────────
# FORMATAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
def fmt_num(valor: float, casas: int = 2) -> str:
    """1234.5 -> '1.234,50' (padrão brasileiro)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_brl(valor: float) -> str:
    return f"R$ {fmt_num(valor, 0 if valor >= 10_000 else 2)}"


# ─────────────────────────────────────────────────────────────────────────────
# HISTÓRICO (guardado na sessão)
# ─────────────────────────────────────────────────────────────────────────────
def registrar_historico(par: str, taxa: float) -> None:
    historico = st.session_state.setdefault("historico", [])
    if historico and historico[0]["par"] == par and historico[0]["taxa"] == taxa:
        return
    historico.insert(0, {"par": par, "taxa": taxa, "hora": datetime.now().strftime("%H:%M")})
    del historico[MAX_HISTORICO:]


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENTES
# ─────────────────────────────────────────────────────────────────────────────
def render_cabecalho() -> None:
    st.markdown(
        '<h1 class="page-title">Conversor e cotação de moedas</h1>'
        '<p class="page-subtitle">Valores em tempo real das principais moedas em relação ao real.</p>',
        unsafe_allow_html=True,
    )


def render_conversor() -> None:
    with st.container(key="conversor"):
        col_valor, col_de, col_para = st.columns([2, 1, 1])
        valor = col_valor.number_input(
            "Valor a converter", min_value=0.01, value=1000.00, step=10.0, format="%.2f"
        )
        origem = col_de.selectbox(
            "De", list(MOEDAS_ORIGEM), format_func=lambda c: f"{c} · {MOEDAS_ORIGEM[c]}"
        )
        destino = col_para.selectbox("Para", ["BRL"], format_func=lambda c: f"{c} · Real brasileiro")

        par = f"{origem}-{destino}"
        info = consultar_cotacoes((par,)).get(chave_par(par))

        if not info:
            st.warning("Não foi possível obter essa cotação agora. Tente novamente em instantes.")
            return

        taxa = float(info["bid"])
        registrar_historico(par.replace("-", " → "), taxa)

        st.markdown(
            '<div class="resultado">'
            '<span class="resultado-rotulo">Resultado</span>'
            f'<span class="resultado-valor">R$ {fmt_num(valor * taxa)}</span>'
            f'<span class="resultado-taxa">1 {origem} = <b>R$ {fmt_num(taxa, 4)}</b>'
            f' · atualizado em {info["create_date"]}</span>'
            "</div>",
            unsafe_allow_html=True,
        )


def card_html(par: str, info: dict | None) -> str:
    moeda = par.split("-")[0]
    nome = MOEDAS_ORIGEM.get(moeda, moeda)
    if not info:
        return (
            f'<div class="card"><div class="card-titulo">{nome} ({moeda})</div>'
            '<div class="card-valor">Indisponível</div></div>'
        )
    variacao = float(info["pctChange"])
    classe, seta = ("up", "▲") if variacao >= 0 else ("down", "▼")
    return (
        '<div class="card">'
        f'<div class="card-titulo">{nome} ({moeda})</div>'
        f'<div class="card-valor">{fmt_brl(float(info["bid"]))}</div>'
        f'<div class="card-var {classe}">{seta} {fmt_num(abs(variacao))}% hoje</div>'
        f'<div class="card-faixa">Mín {fmt_brl(float(info["low"]))} · Máx {fmt_brl(float(info["high"]))}</div>'
        "</div>"
    )


def render_destaques() -> None:
    st.markdown('<h2 class="section-title">Cotações principais</h2>', unsafe_allow_html=True)
    dados = consultar_cotacoes(DESTAQUES)  # uma única requisição para todos
    for coluna, par in zip(st.columns(len(DESTAQUES), gap="medium"), DESTAQUES):
        coluna.markdown(card_html(par, dados.get(chave_par(par))), unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.subheader("Histórico recente")
        historico = st.session_state.get("historico", [])
        if historico:
            for item in historico:
                st.markdown(
                    f'<div class="hist-item"><span>{item["par"]}'
                    f' <span class="hist-hora">{item["hora"]}</span></span>'
                    f'<span class="hist-taxa">{fmt_num(item["taxa"], 4)}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("As conversões que você fizer aparecem aqui.")

        st.write("")
        if st.button("Atualizar cotações", use_container_width=True):
            consultar_cotacoes.clear()
            st.rerun()
        if historico and st.button("Limpar histórico", use_container_width=True):
            st.session_state["historico"] = []
            st.rerun()

        st.divider()
        st.caption("Fonte dos dados: AwesomeAPI. Cotações atualizadas a cada 30 segundos.")


# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    render_cabecalho()
    render_conversor()
    render_destaques()
    render_sidebar()  # por último, para já mostrar a conversão desta execução


main()