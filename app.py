"""
app.py — Interface Streamlit — KrillTech Fin: Sistema de Risco de Crédito Agro
================================================================================
Execute com:  streamlit run app.py
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from mock_data import CLIENTES, LISTA_CLIENTES, OPEN_FINANCE
from collector import coletar_dados_cliente, resumo_cadastral
from agro_risk import calcular_score_agro
from macro_context import (
    calcular_fator_estresse_macro,
    cenario_choque_petroleo,
    buscar_variaveis_com_gemini,
    VARIAVEIS_BASE,
    PARAMETROS_MACRO,
    LIMIAR_ALERTA_ESTRESSE,
)
from scoring_engine import calcular_score_final, cor_rating
from report_generator import gerar_relatorio

# ─── Configuração da Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="KrillTech Fin — Risco de Crédito Agro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Customizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Tipografia: IBM Plex Serif (títulos) + IBM Plex Sans (corpo) —
   referência sutil ao ecossistema IBM watsonx citado no desafio. */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@500;600;700&display=swap');

/* Forçar tema claro uniforme independente do tema selecionado no Streamlit (dark/light) */
:root, [data-theme="dark"], [data-theme="light"], body, .stApp {
    --text-color: #1E2A24 !important;
    --background-color: #FAF8F2 !important;
    --secondary-background-color: #EFE9D8 !important;
    --primary-color: #2F5233 !important;
    background-color: #FAF8F2 !important;
    background: linear-gradient(180deg, #FAF8F2 0%, #F5F2E9 100%) !important;
    color: #1E2A24 !important;
    font-family: 'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Forçar a cor do texto escuro para todos os componentes principais */
.stApp p, .stApp span, .stApp label, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp li, .stApp td, .stApp th, .stApp input, .stApp textarea,
[data-testid="stMarkdownContainer"] *,
[data-testid="stMetricValue"] *,
[data-testid="stMetricLabel"] *,
[data-testid="stMetricDelta"] *,
[data-testid="stCaptionContainer"] *,
[data-testid="stExpander"] *,
[data-baseweb="select"] *,
[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
[data-baseweb="option"] *,
[data-testid="stWidgetLabel"] *,
.stSelectbox *, .stMultiSelect *, .stSlider * {
    color: #1E2A24 !important;
}

/* Sidebar: tom de capa de dossiê, separado por uma régua fina */
[data-testid="stSidebar"] {
    background: #EFE9D8 !important;
    border-right: 1px solid #C9BFA0 !important;
}
[data-testid="stSidebar"] * {
    color: #1E2A24 !important;
}

/* Cards de métricas: régua fina + acento verde à esquerda */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E1DAC5 !important;
    border-left: 3px solid #2F5233 !important;
    border-radius: 8px;
    padding: 16px;
}
[data-testid="stMetric"] * {
    color: #1E2A24 !important;
}

/* Títulos em serifada, cor verde-safra */
h1, h2, h3 {
    font-family: 'IBM Plex Serif', serif !important;
    color: #2F5233 !important;
    font-weight: 600 !important;
}

/* Botão primário: verde-safra sólido, texto pergaminho */
.stButton > button, .stButton > button * {
    background: #2F5233 !important;
    color: #FAF8F2 !important;
    border: 1px solid #223D26 !important;
    border-radius: 6px;
    font-weight: 600;
    font-size: 16px;
    padding: 12px 28px;
    transition: background 0.2s ease;
    width: 100%;
}
.stButton > button:hover {
    background: #223D26 !important;
    border-color: #1a2e1c !important;
}

/* Score badge customizado */
.score-badge {
    display: inline-block;
    padding: 8px 20px;
    border-radius: 8px;
    font-size: 24px;
    font-weight: 700;
    text-align: center;
}

/* Red flag card — tons terrosos por severidade */
.flag-critico, .flag-critico * {
    background: rgba(166, 50, 27, 0.08);
    border-left: 4px solid #A6321B;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #1E2A24 !important;
}
.flag-alto, .flag-alto * {
    background: rgba(168, 85, 31, 0.08);
    border-left: 4px solid #A8551F;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #1E2A24 !important;
}
.flag-medio, .flag-medio * {
    background: rgba(138, 106, 20, 0.08);
    border-left: 4px solid #8A6A14;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #1E2A24 !important;
}

/* Separador */
hr {
    border: none;
    border-top: 1px solid #D9D2C0;
    margin: 24px 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #EFE9D8 !important;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    color: #5B6B5E !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(47, 82, 51, 0.15) !important;
    color: #2F5233 !important;
}
.stTabs [aria-selected="true"] * {
    color: #2F5233 !important;
}

/* Selectbox e Popovers / Dropdowns */
[data-baseweb="select"] > div, [data-baseweb="popover"], [data-baseweb="menu"] {
    background-color: #FFFFFF !important;
}

/* Info boxes */
.info-card, .info-card * {
    background: #FFFFFF;
    border: 1px solid #E1DAC5;
    border-left: 3px solid #2F5233;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
    color: #1E2A24 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/wheat.png",
        width=60,
    )
    st.title("KrillTech Fin")
    st.caption("Sistema de Risco de Crédito Agro")
    st.divider()

    st.markdown("### 📌 Selecionar Cliente")
    cliente_selecionado = st.selectbox(
        "Cliente",
        options=LISTA_CLIENTES,
        label_visibility="collapsed",
    )
    cnpj_selecionado = cliente_selecionado.split(" — ")[0].strip()

    st.divider()
    st.markdown("### ℹ️ Sobre o Sistema")
    st.markdown("""
    Pipeline automatizada de análise de risco de crédito para o agronegócio.

    **Módulos:**
    1. 📂 Coletor & Parser
    2. 🌾 Risco Agro-Climático
    3. 🌐 Contexto Macro
    4. ⚙️ Motor de Scoring
    5. 📄 Gerador de Relatório
    """)
    st.caption("MVP — Dados simulados para demonstração")

# ─── Tabs Principais ─────────────────────────────────────────────────────────
tab_relatorio, tab_simulador, tab_openfinance = st.tabs([
    "📋 Relatório de Risco",
    "🎛️ Simulador de Cenário Macro",
    "🏦 Open Finance",
])


# ===========================================================================
# TAB 1: RELATÓRIO DE RISCO
# ===========================================================================
with tab_relatorio:
    st.markdown("## 📋 Análise de Risco de Crédito")

    col_info, col_btn = st.columns([3, 1])
    with col_info:
        dados_preview = CLIENTES.get(cnpj_selecionado, {})
        st.markdown(f"""
        <div class="info-card">
        🏢 <strong>{dados_preview.get('razao_social', '')}</strong> &nbsp;|&nbsp;
        📍 {dados_preview.get('municipio', '')}, {dados_preview.get('uf', '')} &nbsp;|&nbsp;
        🌱 {dados_preview.get('cultura_principal', '')} &nbsp;|&nbsp;
        📅 {dados_preview.get('anos_atividade', 0)} anos de atividade
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        gerar = st.button("🚀 Gerar Relatório", use_container_width=True)

    # ── Pipeline de análise ─────────────────────────────────────────────────
    if gerar or "ultimo_relatorio" in st.session_state:

        if gerar:
            with st.spinner("⚙️ Executando pipeline de análise..."):
                # Módulo 1: Coletor
                dados_cliente = coletar_dados_cliente(cnpj_selecionado)

                # Módulo 2: Risco Agro
                resultado_agro = calcular_score_agro(
                    dados_cliente["uf"],
                    dados_cliente["cultura_principal"],
                )

                # Módulo 3: Macro
                vars_macro = calcular_fator_estresse_macro(VARIAVEIS_BASE)

                # Módulo 4: Scoring
                resultado_scoring = calcular_score_final(
                    dados_cliente, resultado_agro, vars_macro
                )

                # Módulo 5: Relatório
                relatorio_md = gerar_relatorio(
                    dados_cliente, resultado_agro, vars_macro, resultado_scoring
                )

                # Cache no session_state
                st.session_state["ultimo_relatorio"] = {
                    "dados_cliente": dados_cliente,
                    "resultado_agro": resultado_agro,
                    "vars_macro": vars_macro,
                    "resultado_scoring": resultado_scoring,
                    "relatorio_md": relatorio_md,
                    "cnpj": cnpj_selecionado,
                }

        # Carregar do cache
        cache = st.session_state["ultimo_relatorio"]

        # Se mudou o cliente, limpar cache
        if cache.get("cnpj") != cnpj_selecionado and not gerar:
            st.info("ℹ️ Selecione um cliente e clique em **Gerar Relatório**.")
            st.stop()

        dados_cliente    = cache["dados_cliente"]
        resultado_agro   = cache["resultado_agro"]
        vars_macro       = cache["vars_macro"]
        resultado_scoring = cache["resultado_scoring"]
        relatorio_md     = cache["relatorio_md"]

        st.divider()

        # ── Painel de KPIs ─────────────────────────────────────────────────
        rating     = resultado_scoring["rating"]
        score_adj  = resultado_scoring["score_ajustado"]
        score_idio = resultado_scoring["score_idiossincrático"]
        variacao   = resultado_scoring["variacao_macro"]
        n_flags    = resultado_scoring["n_red_flags"]
        cor        = cor_rating(rating)

        # Score badge (HTML)
        st.markdown(f"""
        <div style="text-align:center; margin: 16px 0 24px 0;">
            <div style="display:inline-block; background:{cor}22; border:2px solid {cor};
                        border-radius:16px; padding:20px 48px;">
                <div style="font-size:14px; color:#4B5563; font-weight:600; margin-bottom:4px;">
                    RATING FINAL
                </div>
                <div style="font-size:56px; font-weight:800; color:{cor}; line-height:1;">
                    {rating}
                </div>
                <div style="font-size:13px; color:#4B5563; margin-top:4px;">
                    {resultado_scoring['descricao_rating']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Métricas em colunas
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric(
            "Score Ajustado",
            f"{score_adj:.0f}",
            f"{variacao:+.0f} (macro)",
            delta_color="inverse",
        )
        m2.metric(
            "Score Idiossincrático",
            f"{score_idio:.0f}",
            "sem ajuste macro",
            delta_color="off",
        )
        m3.metric(
            "Fator de Estresse",
            f"{vars_macro['fator_estresse']:.3f}×",
            "1.000 = neutro",
            delta_color="off",
        )
        m4.metric(
            "Red Flags",
            f"{n_flags}",
            "⛔ CRÍTICO" if resultado_scoring["tem_flag_critica"] else "sem críticos",
            delta_color="inverse" if resultado_scoring["tem_flag_critica"] else "off",
        )
        m5.metric(
            "Limite Sugerido",
            f"R$ {resultado_scoring['limite_credito_brl']:,.0f}" if rating != "D"
                else "NEGADO",
            f"{resultado_scoring['limite_credito_pct']:.0%} do fat.",
            delta_color="off",
        )

        st.divider()

        # ── Gráficos Lado a Lado ───────────────────────────────────────────
        col_radar, col_gauge, col_comparativo = st.columns([2, 2, 2])

        with col_radar:
            st.markdown("##### 🕸️ Scores por Dimensão")
            dims = resultado_scoring["scores_dimensao"]
            categorias = list(dims.keys())
            valores    = list(dims.values()) + [list(dims.values())[0]]  # fechar radar
            categorias_plot = categorias + [categorias[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=valores,
                theta=categorias_plot,
                fill="toself",
                fillcolor=f"{cor}33",
                line=dict(color=cor, width=2),
                name="Score",
                hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(color="#5B6B5E", size=10),
                        gridcolor="rgba(30,42,36,0.12)",
                    ),
                    angularaxis=dict(
                        tickfont=dict(color="#1E2A24", size=11),
                        gridcolor="rgba(30,42,36,0.12)",
                    ),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1E2A24"),
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                height=280,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_gauge:
            st.markdown("##### 🎯 Score Final (Gauge)")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score_adj,
                delta={
                    "reference": score_idio,
                    "valueformat": ".0f",
                    "prefix": "vs idio: ",
                },
                gauge={
                    "axis": {"range": [0, 1000], "tickcolor": "#5B6B5E"},
                    "bar": {"color": cor, "thickness": 0.25},
                    "bgcolor": "rgba(0,0,0,0)",
                    "bordercolor": "rgba(30,42,36,0.15)",
                    "steps": [
                        {"range": [0,   400], "color": "rgba(166,50,27,0.12)"},
                        {"range": [400, 600], "color": "rgba(168,85,31,0.12)"},
                        {"range": [600, 800], "color": "rgba(138,106,20,0.12)"},
                        {"range": [800,1000], "color": "rgba(47,82,51,0.12)"},
                    ],
                    "threshold": {
                        "line": {"color": "#1E2A24", "width": 3},
                        "thickness": 0.75,
                        "value": score_idio,
                    },
                },
                number={"font": {"color": cor, "size": 40}},
                title={"text": f"Rating {rating}", "font": {"color": "#1E2A24", "size": 14}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1E2A24"),
                height=280,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_comparativo:
            st.markdown("##### ⚖️ Idiossincrático vs. Ajustado")
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=["Score\nIdiossincrático", "Score\nAjustado (macro)"],
                y=[score_idio, score_adj],
                marker_color=["#1B2A41", cor],
                text=[f"{score_idio:.0f}", f"{score_adj:.0f}"],
                textposition="outside",
                textfont=dict(color="#1E2A24", size=16, family="IBM Plex Sans"),
                width=0.5,
            ))
            # Linha de referência: limite de faixa
            fig_bar.add_hline(
                y=800, line_dash="dot", line_color="#2F5233",
                annotation_text="A ≥ 800", annotation_font_color="#2F5233",
            )
            fig_bar.add_hline(
                y=600, line_dash="dot", line_color="#8A6A14",
                annotation_text="B ≥ 600", annotation_font_color="#8A6A14",
            )
            fig_bar.add_hline(
                y=400, line_dash="dot", line_color="#A8551F",
                annotation_text="C ≥ 400", annotation_font_color="#A8551F",
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(
                    range=[0, 1100],
                    gridcolor="rgba(30,42,36,0.10)",
                    tickcolor="#5B6B5E",
                    tickfont=dict(color="#5B6B5E"),
                ),
                xaxis=dict(tickfont=dict(color="#1E2A24", size=12)),
                font=dict(color="#1E2A24"),
                height=280,
                margin=dict(l=10, r=10, t=20, b=10),
                showlegend=False,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ── Red Flags ─────────────────────────────────────────────────────
        st.markdown("### 🚦 Red Flags")
        flags = resultado_scoring["red_flags"]
        if not flags:
            st.success("✅ Nenhum red flag identificado. Perfil dentro dos parâmetros normais.")
        else:
            for flag in flags:
                sev = flag["severidade"]
                css_class = {
                    "CRÍTICO": "flag-critico",
                    "ALTO":    "flag-alto",
                    "MÉDIO":   "flag-medio",
                }.get(sev, "flag-medio")

                st.markdown(
                    f'<div class="{css_class}">'
                    f'<strong>[{sev}]</strong> <code>{flag["codigo"]}</code><br>'
                    f'{flag["mensagem"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.divider()

        # ── Relatório Completo (Markdown) ──────────────────────────────────
        with st.expander("📄 Ver Relatório Completo em Markdown", expanded=False):
            st.markdown(relatorio_md)

            # Botão de download
            st.download_button(
                label="⬇️ Baixar Relatório (.md)",
                data=relatorio_md.encode("utf-8"),
                file_name=f"relatorio_risco_{cnpj_selecionado.replace('/', '_').replace('.', '')}.md",
                mime="text/markdown",
            )

    else:
        # Estado inicial
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color: #5a7a9a;">
            <div style="font-size:64px;">🌾</div>
            <h3 style="color:#5a7a9a;">Selecione um cliente e clique em Gerar Relatório</h3>
            <p>A pipeline irá executar os 5 módulos de análise e gerar o score completo.</p>
        </div>
        """, unsafe_allow_html=True)


# ===========================================================================
# TAB 2: SIMULADOR DE CENÁRIO MACRO
# ===========================================================================

# ── Inicializar session_state dos sliders (uma vez) ─────────────────────
for _k, _v in [
    ("sim_cambio",  VARIAVEIS_BASE["cambio_usd_brl"]),
    ("sim_petro",   VARIAVEIS_BASE["petroleo_brent_usd"]),
    ("sim_fertil",  VARIAVEIS_BASE["indice_fertilizantes"]),
    ("sim_selic",   VARIAVEIS_BASE["selic_pct"]),
    ("sim_geop",    VARIAVEIS_BASE["risco_geopolitico"]),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Callbacks dos presets (executam ANTES do rerun dos widgets) ──────────
def _preset_base():
    st.session_state["sim_cambio"]  = VARIAVEIS_BASE["cambio_usd_brl"]
    st.session_state["sim_petro"]   = VARIAVEIS_BASE["petroleo_brent_usd"]
    st.session_state["sim_fertil"]  = VARIAVEIS_BASE["indice_fertilizantes"]
    st.session_state["sim_selic"]   = VARIAVEIS_BASE["selic_pct"]
    st.session_state["sim_geop"]    = VARIAVEIS_BASE["risco_geopolitico"]

def _preset_choque():
    choque = cenario_choque_petroleo(1.65)
    v = choque["variaveis_cenario"]
    st.session_state["sim_cambio"]  = v["cambio_usd_brl"]
    st.session_state["sim_petro"]   = v["petroleo_brent_usd"]
    st.session_state["sim_fertil"]  = v["indice_fertilizantes"]
    st.session_state["sim_selic"]   = v["selic_pct"]
    st.session_state["sim_geop"]    = v["risco_geopolitico"]

def _preset_selic():
    st.session_state["sim_cambio"]  = 5.90
    st.session_state["sim_petro"]   = 88.0
    st.session_state["sim_fertil"]  = 155.0
    st.session_state["sim_selic"]   = 16.0
    st.session_state["sim_geop"]    = 30.0

def _preset_cambio():
    st.session_state["sim_cambio"]  = 7.20
    st.session_state["sim_petro"]   = 90.0
    st.session_state["sim_fertil"]  = 160.0
    st.session_state["sim_selic"]   = 11.75
    st.session_state["sim_geop"]    = 35.0


with tab_simulador:
    st.markdown("## 🎛️ Simulador de Cenário Macroeconômico")
    st.markdown(
        "Ajuste as variáveis macro abaixo e veja o impacto **em tempo real** "
        "sobre o score do cliente selecionado."
    )

    # ── Preset de Cenários ──────────────────────────────────────────────────
    st.markdown("#### ⚡ Cenários Pré-definidos 🔗")
    pc1, pc2, pc3, pc4 = st.columns(4)

    with pc1:
        st.button("🟢 Base (Atual)", use_container_width=True, on_click=_preset_base)
    with pc2:
        st.button("🔴 Choque Petróleo (+65%)", use_container_width=True, on_click=_preset_choque)
    with pc3:
        st.button("🟠 Selic Alta (16%)", use_container_width=True, on_click=_preset_selic)
    with pc4:
        st.button("🟡 Câmbio Estressado (R$7,20)", use_container_width=True, on_click=_preset_cambio)

    st.divider()

    # ── Busca de Dados Reais com IA ─────────────────────────────────────────
    st.markdown("#### 🤖 Dados Reais via IA (Gemini)")
    col_ia_btn, col_ia_info = st.columns([1, 3])

    with col_ia_btn:
        buscar_ia = st.button("🔍 Buscar Dados Atuais", use_container_width=True)

    with col_ia_info:
        st.caption(
            "Usa o Google Gemini com busca na web para obter os valores "
            "macroeconômicos mais recentes e preencher os sliders automaticamente."
        )

    if buscar_ia:
        with st.spinner("🌐 Consultando Gemini + Google Search..."):
            resultado_ia = buscar_variaveis_com_gemini()

        if resultado_ia and "erro" not in resultado_ia:
            st.session_state["sim_cambio"]  = resultado_ia["cambio_usd_brl"]
            st.session_state["sim_petro"]   = resultado_ia["petroleo_brent_usd"]
            st.session_state["sim_fertil"]  = resultado_ia["indice_fertilizantes"]
            st.session_state["sim_selic"]   = resultado_ia["selic_pct"]
            st.session_state["sim_geop"]    = resultado_ia["risco_geopolitico"]

            fonte = resultado_ia.get("fonte", "Google Search via Gemini")
            data_c = resultado_ia.get("data_consulta", "—")

            st.success(
                f"✅ Variáveis atualizadas com sucesso! "
                f"Fonte: {fonte} | Data: {data_c}"
            )
            st.rerun()
        elif resultado_ia and "erro" in resultado_ia:
            st.error(f"❌ Erro na consulta: {resultado_ia['erro']}")
        else:
            st.warning("⚠️ Não foi possível obter os dados. Tente novamente.")

    st.divider()

    # ── Sliders (com key vinculado ao session_state) ────────────────────────
    st.markdown("#### 🎚️ Ajuste Manual das Variáveis")

    col_sl1, col_sl2 = st.columns(2)

    with col_sl1:
        cambio = st.slider(
            "💵 Câmbio USD/BRL (R$/US$)",
            min_value=3.5, max_value=9.0, step=0.05,
            key="sim_cambio",
            format="R$ %.2f",
        )
        petroleo = st.slider(
            "🛢️ Petróleo Brent (US$/barril)",
            min_value=40.0, max_value=200.0, step=1.0,
            key="sim_petro",
            format="US$ %.0f",
        )
        fertilizantes = st.slider(
            "🧪 Índice de Fertilizantes (base 100)",
            min_value=80.0, max_value=350.0, step=5.0,
            key="sim_fertil",
            format="%.0f pts",
        )

    with col_sl2:
        selic = st.slider(
            "🏦 Taxa Selic (% a.a.)",
            min_value=5.0, max_value=20.0, step=0.25,
            key="sim_selic",
            format="%.2f%%",
        )
        risco_geop = st.slider(
            "🌍 Índice de Risco Geopolítico (0–100)",
            min_value=0.0, max_value=100.0, step=1.0,
            key="sim_geop",
            format="%.0f",
        )

    # ── Cálculo em Tempo Real ────────────────────────────────────────────────
    vars_simuladas = {
        "cambio_usd_brl":      cambio,
        "petroleo_brent_usd":  petroleo,
        "indice_fertilizantes": fertilizantes,
        "selic_pct":           selic,
        "risco_geopolitico":   risco_geop,
    }

    resultado_macro_sim = calcular_fator_estresse_macro(vars_simuladas)
    fator_sim = resultado_macro_sim["fator_estresse"]

    # Calcular score simulado para o cliente selecionado
    dados_cliente_sim = coletar_dados_cliente(cnpj_selecionado)
    resultado_agro_sim = calcular_score_agro(
        dados_cliente_sim["uf"],
        dados_cliente_sim["cultura_principal"],
    )
    resultado_scoring_sim = calcular_score_final(
        dados_cliente_sim, resultado_agro_sim, resultado_macro_sim
    )

    # Valores base para comparação
    resultado_macro_base = calcular_fator_estresse_macro(VARIAVEIS_BASE)
    resultado_scoring_base = calcular_score_final(
        dados_cliente_sim, resultado_agro_sim, resultado_macro_base
    )

    st.divider()

    # ── Painel de Resultados da Simulação ────────────────────────────────────
    st.markdown(f"#### 📊 Impacto sobre: **{dados_cliente_sim.get('nome_fantasia', '')}**")

    rating_sim   = resultado_scoring_sim["rating"]
    score_sim    = resultado_scoring_sim["score_ajustado"]
    score_base_v = resultado_scoring_base["score_ajustado"]
    delta_score  = score_sim - score_base_v
    cor_sim      = cor_rating(rating_sim)

    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.metric(
        "Fator de Estresse Macro",
        f"{fator_sim:.4f}×",
        f"{fator_sim - resultado_macro_base['fator_estresse']:+.4f} vs base",
        delta_color="inverse",
    )
    sm2.metric(
        "Score Simulado",
        f"{score_sim:.0f}",
        f"{delta_score:+.0f} vs base ({score_base_v:.0f})",
        delta_color="inverse",
    )
    sm3.metric(
        "Rating Simulado",
        rating_sim,
        resultado_scoring_sim["descricao_rating"],
        delta_color="off",
    )
    sm4.metric(
        "Red Flags",
        resultado_scoring_sim["n_red_flags"],
        "⛔ CRÍTICO" if resultado_scoring_sim["tem_flag_critica"] else "sem críticos",
        delta_color="inverse" if resultado_scoring_sim["tem_flag_critica"] else "off",
    )

    # Alerta visual se acima do limiar
    if resultado_macro_sim["acima_do_limiar"]:
        st.markdown(
            f'<div class="flag-alto" style="margin-top:12px;">'
            f'🌐 <strong>Alerta Macro Ativo:</strong> Fator de estresse {fator_sim:.4f}× '
            f'ultrapassou o limiar de {LIMIAR_ALERTA_ESTRESSE:.2f}×. '
            f'Risco setorial elevado — revisar exposições ao setor antes de novas concessões.'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Gráfico: Contribuição por Variável ───────────────────────────────────
    col_contrib, col_waterfall = st.columns([1, 1])

    with col_contrib:
        st.markdown("##### 🧩 Estresse por Variável Macro")
        detalhes = resultado_macro_sim["detalhes_por_variavel"]
        df_contrib = pd.DataFrame([
            {
                "Variável": d["descricao"],
                "Estresse (norm.)": d["stress_normalizado"],
                "Contribuição": d["contribuicao_ponderada"],
            }
            for d in detalhes.values()
        ]).sort_values("Contribuição", ascending=True)

        fig_contrib = px.bar(
            df_contrib,
            x="Contribuição",
            y="Variável",
            orientation="h",
            color="Contribuição",
            color_continuous_scale=["#2F5233", "#8A6A14", "#A6321B"],
            range_color=[0, 0.30],
            text=df_contrib["Estresse (norm.)"].map(lambda x: f"{x:.0%}"),
        )
        fig_contrib.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1E2A24"),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="rgba(30,42,36,0.10)", tickformat=".3f"),
            yaxis=dict(tickfont=dict(size=12)),
            margin=dict(l=0, r=10, t=10, b=10),
            height=280,
            showlegend=False,
        )
        st.plotly_chart(fig_contrib, use_container_width=True)

    with col_waterfall:
        st.markdown("##### 🌊 Score: Base → Simulado")

        # Waterfall: idio base → ajuste macro base → ajuste macro simulado → score final sim
        delta_macro_base = resultado_scoring_base["variacao_macro"]
        delta_macro_extra = delta_score - delta_macro_base  # diferença adicional da simulação

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Score\nIdiossincrático", "Ajuste\nMacro Base", "Δ Simulação\nMacro", "Score\nFinal Sim."],
            y=[
                resultado_scoring_sim["score_idiossincrático"],
                delta_macro_base,
                delta_macro_extra,
                0,  # total calculado automaticamente
            ],
            text=[
                f"{resultado_scoring_sim['score_idiossincrático']:.0f}",
                f"{delta_macro_base:+.0f}",
                f"{delta_macro_extra:+.0f}",
                f"{score_sim:.0f}",
            ],
            textposition="outside",
            connector={"line": {"color": "rgba(30,42,36,0.25)"}},
            increasing={"marker": {"color": "#2F5233"}},
            decreasing={"marker": {"color": "#A6321B"}},
            totals={"marker": {"color": cor_sim}},
        ))
        fig_wf.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1E2A24"),
            yaxis=dict(
                range=[0, 1100],
                gridcolor="rgba(30,42,36,0.10)",
                tickcolor="#5B6B5E",
            ),
            xaxis=dict(tickfont=dict(size=11)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    st.divider()

    # ── Tabela comparativa: todos os clientes ────────────────────────────────
    st.markdown("##### 📊 Impacto do Cenário Simulado — Todos os Clientes")

    rows = []
    for cnpj, cliente in CLIENTES.items():
        dc = coletar_dados_cliente(cnpj)
        ra = calcular_score_agro(dc["uf"], dc["cultura_principal"])

        s_base = calcular_score_final(dc, ra, resultado_macro_base)
        s_sim  = calcular_score_final(dc, ra, resultado_macro_sim)

        rows.append({
            "Cliente": cliente["nome_fantasia"],
            "UF": cliente["uf"],
            "Cultura": cliente["cultura_principal"],
            "Score Base": s_base["score_ajustado"],
            "Score Simulado": s_sim["score_ajustado"],
            "Δ Score": s_sim["score_ajustado"] - s_base["score_ajustado"],
            "Rating Base": s_base["rating"],
            "Rating Sim.": s_sim["rating"],
        })

    df_comp = pd.DataFrame(rows).sort_values("Δ Score")

    def colorir_delta(val):
        if val < -30:
            return "color: #A6321B; font-weight:600"
        elif val < 0:
            return "color: #A8551F"
        elif val > 0:
            return "color: #2F5233"
        return "color: #5B6B5E"

    def colorir_rating(val):
        cores = {"A": "#2F5233", "B": "#8A6A14", "C": "#A8551F", "D": "#A6321B"}
        c = cores.get(val, "#5B6B5E")
        return f"color: {c}; font-weight:700"

    styled_df = (
        df_comp.style
        .map(colorir_delta, subset=["Δ Score"])
        .map(colorir_rating, subset=["Rating Base", "Rating Sim."])
        .format({
            "Score Base": "{:.0f}",
            "Score Simulado": "{:.0f}",
            "Δ Score": "{:+.0f}",
        })
    )

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ===========================================================================
# TAB 3: OPEN FINANCE
# ===========================================================================
with tab_openfinance:
    st.markdown("## 🏦 Open Finance — Indicadores Financeiros")
    st.markdown(
        "Dados obtidos via **Open Finance (Open Banking Brasil)** com consentimento "
        "do cliente. Indicadores de saúde financeira e alerta precoce de inadimplência."
    )

    of_data = OPEN_FINANCE.get(cnpj_selecionado)

    if not of_data:
        st.info("ℹ️ Dados de Open Finance não disponíveis para este cliente.")
    elif not of_data.get("consentimento_ativo"):
        st.warning("⚠️ Consentimento de Open Finance não ativo para este cliente.")
    else:
        dados_preview_of = CLIENTES.get(cnpj_selecionado, {})
        st.markdown(f"""
        <div class="info-card">
        🏢 <strong>{dados_preview_of.get('nome_fantasia', '')}</strong> &nbsp;|&nbsp;
        🔗 Conectado a: {', '.join(of_data['instituicoes_conectadas'])} &nbsp;|&nbsp;
        📊 {of_data['operacoes_credito_ativas']} operações de crédito ativas
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Alerta de Inadimplência ─────────────────────────────────────────
        risco_inad = of_data["risco_inadimplencia"]
        alerta = of_data["alerta_inadimplencia"]
        meses_risco = of_data.get("meses_ate_risco_estimado")

        if risco_inad == "CRÍTICO":
            meses_txt = f"**{meses_risco} mês**" if meses_risco == 1 else f"**{meses_risco} meses**"
            st.markdown(
                f'<div class="flag-critico" style="font-size:16px; padding:20px;">'
                f'🚨 <strong>ALERTA CRÍTICO DE INADIMPLÊNCIA</strong><br><br>'
                f'Estimativa de tempo até inadimplência: {meses_txt}.<br>'
                f'{of_data["observacao"]}'
                f'</div>',
                unsafe_allow_html=True,
            )
        elif risco_inad == "ELEVADO":
            st.markdown(
                f'<div class="flag-alto" style="font-size:15px; padding:18px;">'
                f'⚠️ <strong>RISCO ELEVADO DE INADIMPLÊNCIA</strong><br><br>'
                f'Estimativa: {meses_risco} meses até risco concreto.<br>'
                f'{of_data["observacao"]}'
                f'</div>',
                unsafe_allow_html=True,
            )
        elif risco_inad == "MODERADO":
            st.markdown(
                f'<div class="flag-medio" style="font-size:14px; padding:16px;">'
                f'🟡 <strong>RISCO MODERADO</strong> — {of_data["observacao"]}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # ── KPIs principais ─────────────────────────────────────────────────
        st.markdown("#### 📊 Indicadores de Saúde Financeira")
        of1, of2, of3, of4, of5 = st.columns(5)

        # Cor do comprometimento
        comp_pct = of_data["comprometimento_renda_pct"]

        of1.metric(
            "Saldo em Conta",
            f"R$ {of_data['saldo_conta_corrente_brl']:,.0f}",
            f"{of_data['tendencia_saldo'].replace('_', ' ')}",
            delta_color="normal" if of_data["tendencia_saldo"] == "crescente" else "inverse",
        )
        of2.metric(
            "Comprometimento de Renda",
            f"{comp_pct:.1f}%",
            "saudável" if comp_pct < 35 else ("atenção" if comp_pct < 60 else "CRÍTICO"),
            delta_color="off" if comp_pct < 35 else "inverse",
        )
        of3.metric(
            "Utilização de Crédito",
            f"{of_data['utilizacao_credito_pct']:.1f}%",
            f"R$ {of_data['limite_utilizado_brl']:,.0f} / {of_data['limite_credito_total_brl']:,.0f}",
            delta_color="off",
        )
        of4.metric(
            "Cobertura de Dívida",
            f"{of_data['indice_cobertura_divida']:.2f}×",
            "adequado" if of_data["indice_cobertura_divida"] >= 1.5 else "insuficiente",
            delta_color="off" if of_data["indice_cobertura_divida"] >= 1.5 else "inverse",
        )
        of5.metric(
            "Pontualidade",
            f"{of_data['score_pontualidade']}/100",
            f"{of_data['parcelas_em_dia']} em dia",
            delta_color="off",
        )

        st.divider()

        # ── Detalhes de atrasos e fluxo ─────────────────────────────────────
        col_atrasos, col_fluxo = st.columns(2)

        with col_atrasos:
            st.markdown("##### 🚦 Histórico de Parcelas")
            total_parcelas = (
                of_data["parcelas_em_dia"]
                + of_data["parcelas_atrasadas_30d"]
                + of_data["parcelas_atrasadas_60d"]
                + of_data["parcelas_atrasadas_90d"]
            )

            atraso_data = pd.DataFrame({
                "Status": ["Em dia", "Atraso 30d", "Atraso 60d", "Atraso 90d+"],
                "Parcelas": [
                    of_data["parcelas_em_dia"],
                    of_data["parcelas_atrasadas_30d"],
                    of_data["parcelas_atrasadas_60d"],
                    of_data["parcelas_atrasadas_90d"],
                ],
            })

            cores_atraso = ["#2F5233", "#8A6A14", "#A8551F", "#A6321B"]

            fig_atraso = px.bar(
                atraso_data,
                x="Status",
                y="Parcelas",
                color="Status",
                color_discrete_sequence=cores_atraso,
                text="Parcelas",
            )
            fig_atraso.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1E2A24"),
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                height=250,
                yaxis=dict(gridcolor="rgba(30,42,36,0.10)"),
            )
            fig_atraso.update_traces(textposition="outside")
            st.plotly_chart(fig_atraso, use_container_width=True)

        with col_fluxo:
            st.markdown("##### 💰 Fluxo de Caixa Mensal")
            receita = of_data["receita_media_mensal_brl"]
            despesa = of_data["despesa_media_mensal_brl"]
            saldo_livre = receita - despesa

            fluxo_data = pd.DataFrame({
                "Tipo": ["Receita", "Despesa", "Saldo Livre"],
                "Valor": [receita, despesa, saldo_livre],
            })

            cor_saldo = "#2F5233" if saldo_livre > 0 else "#A6321B"
            cores_fluxo = ["#2F5233", "#A8551F", cor_saldo]

            fig_fluxo = px.bar(
                fluxo_data,
                x="Tipo",
                y="Valor",
                color="Tipo",
                color_discrete_sequence=cores_fluxo,
                text=fluxo_data["Valor"].map(lambda x: f"R$ {x:,.0f}"),
            )
            fig_fluxo.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1E2A24"),
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                height=250,
                yaxis=dict(gridcolor="rgba(30,42,36,0.10)"),
            )
            fig_fluxo.update_traces(textposition="outside")
            st.plotly_chart(fig_fluxo, use_container_width=True)

        st.divider()

        # ── Evolução do saldo (gráfico de tendência simulado) ───────────────
        st.markdown("##### 📈 Tendência de Saldo — Últimos 6 Meses (simulado)")
        saldo_atual = of_data["saldo_conta_corrente_brl"]
        saldo_3m = of_data["saldo_3_meses_atras_brl"]

        # Interpolar 6 pontos de saldo simulado
        import random
        random.seed(hash(cnpj_selecionado))
        tendencia = of_data["tendencia_saldo"]
        if tendencia in ("queda_acentuada", "colapso"):
            base_6m = saldo_3m * 1.6
            pontos = [base_6m]
            for i in range(1, 6):
                pontos.append(pontos[-1] * random.uniform(0.60, 0.85))
            pontos[5] = saldo_atual
        elif tendencia == "leve_queda":
            base_6m = saldo_3m * 1.15
            pontos = [base_6m]
            for i in range(1, 6):
                pontos.append(pontos[-1] * random.uniform(0.92, 1.02))
            pontos[5] = saldo_atual
        else:  # crescente ou estável
            base_6m = saldo_atual * 0.7
            pontos = [base_6m]
            for i in range(1, 6):
                pontos.append(pontos[-1] * random.uniform(1.02, 1.12))
            pontos[5] = saldo_atual

        meses_labels = ["6m atrás", "5m atrás", "4m atrás", "3m atrás", "2m atrás", "Atual"]
        df_saldo = pd.DataFrame({"Mês": meses_labels, "Saldo (R$)": pontos})

        cor_linha = "#2F5233" if tendencia == "crescente" else (
            "#A6321B" if tendencia in ("queda_acentuada", "colapso") else "#8A6A14"
        )

        fig_saldo = px.line(
            df_saldo, x="Mês", y="Saldo (R$)",
            markers=True,
            text=df_saldo["Saldo (R$)"].map(lambda x: f"R$ {x:,.0f}"),
        )
        fig_saldo.update_traces(
            line_color=cor_linha, line_width=3,
            textposition="top center",
            marker=dict(size=8),
        )
        fig_saldo.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1E2A24"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=280,
            yaxis=dict(gridcolor="rgba(30,42,36,0.10)"),
            showlegend=False,
        )
        st.plotly_chart(fig_saldo, use_container_width=True)

        st.divider()

        # ── Resumo de ocorrências ────────────────────────────────────────────
        st.markdown("##### 📋 Ocorrências nos Últimos 12 Meses")
        oc1, oc2, oc3 = st.columns(3)
        oc1.metric("Cheques Devolvidos", of_data["cheque_devolvido_12m"])
        oc2.metric("Protestos", of_data["protestos_12m"])
        oc3.metric("Instituições c/ Dívida", of_data["qtd_instituicoes_com_divida"])

        # ── Rodapé ──────────────────────────────────────────────────────────
        st.divider()
        st.caption(
            "MVP — Dados simulados para demonstração. Em produção, os dados seriam "
            "obtidos via APIs do ecossistema Open Finance do Banco Central do Brasil, "
            "com consentimento explícito do cliente (fase 4 — dados de operações de crédito)."
        )
