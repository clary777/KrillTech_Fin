"""
app.py — Interface Streamlit — KrillTech Fin: Sistema de Risco de Crédito Agro
================================================================================
Execute com:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from mock_data import CLIENTES, LISTA_CLIENTES
from collector import coletar_dados_cliente, resumo_cadastral
from agro_risk import calcular_score_agro
from macro_context import (
    calcular_fator_estresse_macro,
    cenario_choque_petroleo,
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
/* Fonte e fundo */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Fundo escuro */
.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 50%, #0a1628 100%);
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #111e30 100%);
    border-right: 1px solid #1e3a5f;
}

/* Cards de métricas */
[data-testid="stMetric"] {
    background: rgba(30, 58, 95, 0.4);
    border: 1px solid rgba(100, 160, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    backdrop-filter: blur(10px);
}

/* Títulos */
h1, h2, h3 {
    color: #64b5f6 !important;
    font-weight: 600;
}

/* Botão primário */
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 16px;
    padding: 12px 28px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(21, 101, 192, 0.4);
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1976d2, #1565c0);
    box-shadow: 0 6px 20px rgba(21, 101, 192, 0.6);
    transform: translateY(-1px);
}

/* Score badge customizado */
.score-badge {
    display: inline-block;
    padding: 8px 20px;
    border-radius: 50px;
    font-size: 24px;
    font-weight: 700;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

/* Red flag card */
.flag-critico {
    background: rgba(255, 68, 68, 0.15);
    border-left: 4px solid #ff4444;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
}
.flag-alto {
    background: rgba(255, 136, 0, 0.15);
    border-left: 4px solid #ff8800;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
}
.flag-medio {
    background: rgba(255, 187, 51, 0.15);
    border-left: 4px solid #ffbb33;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
}

/* Separador */
hr {
    border: none;
    border-top: 1px solid rgba(100, 160, 255, 0.2);
    margin: 24px 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(13, 27, 42, 0.8);
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #90caf9;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(21, 101, 192, 0.5) !important;
    color: white !important;
}

/* Info boxes */
.info-card {
    background: rgba(21, 101, 192, 0.1);
    border: 1px solid rgba(100, 160, 255, 0.25);
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
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
tab_relatorio, tab_simulador = st.tabs([
    "📋 Relatório de Risco",
    "🎛️ Simulador de Cenário Macro",
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
                <div style="font-size:14px; color:#aaa; font-weight:500; margin-bottom:4px;">
                    RATING FINAL
                </div>
                <div style="font-size:56px; font-weight:800; color:{cor}; line-height:1;">
                    {rating}
                </div>
                <div style="font-size:13px; color:#ccc; margin-top:4px;">
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
                        tickfont=dict(color="#aaa", size=10),
                        gridcolor="rgba(255,255,255,0.1)",
                    ),
                    angularaxis=dict(
                        tickfont=dict(color="#ddd", size=11),
                        gridcolor="rgba(255,255,255,0.1)",
                    ),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ddd"),
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
                    "axis": {"range": [0, 1000], "tickcolor": "#aaa"},
                    "bar": {"color": cor, "thickness": 0.25},
                    "bgcolor": "rgba(0,0,0,0)",
                    "bordercolor": "rgba(255,255,255,0.1)",
                    "steps": [
                        {"range": [0,   400], "color": "rgba(255,68,68,0.15)"},
                        {"range": [400, 600], "color": "rgba(255,136,0,0.15)"},
                        {"range": [600, 800], "color": "rgba(255,187,51,0.15)"},
                        {"range": [800,1000], "color": "rgba(0,200,81,0.15)"},
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 3},
                        "thickness": 0.75,
                        "value": score_idio,
                    },
                },
                number={"font": {"color": cor, "size": 40}},
                title={"text": f"Rating {rating}", "font": {"color": "#ddd", "size": 14}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ddd"),
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
                marker_color=["#42a5f5", cor],
                text=[f"{score_idio:.0f}", f"{score_adj:.0f}"],
                textposition="outside",
                textfont=dict(color="white", size=16, family="Inter"),
                width=0.5,
            ))
            # Linha de referência: limite de faixa
            fig_bar.add_hline(
                y=800, line_dash="dot", line_color="#00C851",
                annotation_text="A ≥ 800", annotation_font_color="#00C851",
            )
            fig_bar.add_hline(
                y=600, line_dash="dot", line_color="#FFBB33",
                annotation_text="B ≥ 600", annotation_font_color="#FFBB33",
            )
            fig_bar.add_hline(
                y=400, line_dash="dot", line_color="#FF8800",
                annotation_text="C ≥ 400", annotation_font_color="#FF8800",
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(
                    range=[0, 1100],
                    gridcolor="rgba(255,255,255,0.08)",
                    tickcolor="#aaa",
                    tickfont=dict(color="#aaa"),
                ),
                xaxis=dict(tickfont=dict(color="#ddd", size=12)),
                font=dict(color="#ddd"),
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
with tab_simulador:
    st.markdown("## 🎛️ Simulador de Cenário Macroeconômico")
    st.markdown(
        "Ajuste as variáveis macro abaixo e veja o impacto **em tempo real** "
        "sobre o score do cliente selecionado."
    )

    # ── Preset de Cenários ──────────────────────────────────────────────────
    st.markdown("#### ⚡ Cenários Pré-definidos")
    pc1, pc2, pc3, pc4 = st.columns(4)

    with pc1:
        if st.button("🟢 Base (Atual)", use_container_width=True):
            st.session_state["sim_cambio"]  = VARIAVEIS_BASE["cambio_usd_brl"]
            st.session_state["sim_petro"]   = VARIAVEIS_BASE["petroleo_brent_usd"]
            st.session_state["sim_fertil"]  = VARIAVEIS_BASE["indice_fertilizantes"]
            st.session_state["sim_selic"]   = VARIAVEIS_BASE["selic_pct"]
            st.session_state["sim_geop"]    = VARIAVEIS_BASE["risco_geopolitico"]

    with pc2:
        if st.button("🔴 Choque Petróleo (+65%)", use_container_width=True):
            choque = cenario_choque_petroleo(1.65)
            v = choque["variaveis_cenario"]
            st.session_state["sim_cambio"]  = v["cambio_usd_brl"]
            st.session_state["sim_petro"]   = v["petroleo_brent_usd"]
            st.session_state["sim_fertil"]  = v["indice_fertilizantes"]
            st.session_state["sim_selic"]   = v["selic_pct"]
            st.session_state["sim_geop"]    = v["risco_geopolitico"]

    with pc3:
        if st.button("🟠 Selic Alta (16%)", use_container_width=True):
            st.session_state["sim_cambio"]  = 5.90
            st.session_state["sim_petro"]   = 88.0
            st.session_state["sim_fertil"]  = 155.0
            st.session_state["sim_selic"]   = 16.0
            st.session_state["sim_geop"]    = 30.0

    with pc4:
        if st.button("🟡 Câmbio Estressado (R$7,20)", use_container_width=True):
            st.session_state["sim_cambio"]  = 7.20
            st.session_state["sim_petro"]   = 90.0
            st.session_state["sim_fertil"]  = 160.0
            st.session_state["sim_selic"]   = 11.75
            st.session_state["sim_geop"]    = 35.0

    st.divider()

    # ── Sliders ─────────────────────────────────────────────────────────────
    st.markdown("#### 🎚️ Ajuste Manual das Variáveis")

    col_sl1, col_sl2 = st.columns(2)

    with col_sl1:
        cambio = st.slider(
            "💵 Câmbio USD/BRL (R$/US$)",
            min_value=3.5, max_value=9.0, step=0.05,
            value=float(st.session_state.get("sim_cambio", VARIAVEIS_BASE["cambio_usd_brl"])),
            format="R$ %.2f",
        )
        petroleo = st.slider(
            "🛢️ Petróleo Brent (US$/barril)",
            min_value=40.0, max_value=200.0, step=1.0,
            value=float(st.session_state.get("sim_petro", VARIAVEIS_BASE["petroleo_brent_usd"])),
            format="US$ %.0f",
        )
        fertilizantes = st.slider(
            "🧪 Índice de Fertilizantes (base 100)",
            min_value=80.0, max_value=350.0, step=5.0,
            value=float(st.session_state.get("sim_fertil", VARIAVEIS_BASE["indice_fertilizantes"])),
            format="%.0f pts",
        )

    with col_sl2:
        selic = st.slider(
            "🏦 Taxa Selic (% a.a.)",
            min_value=5.0, max_value=20.0, step=0.25,
            value=float(st.session_state.get("sim_selic", VARIAVEIS_BASE["selic_pct"])),
            format="%.2f%%",
        )
        risco_geop = st.slider(
            "🌍 Índice de Risco Geopolítico (0–100)",
            min_value=0.0, max_value=100.0, step=1.0,
            value=float(st.session_state.get("sim_geop", VARIAVEIS_BASE["risco_geopolitico"])),
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
            color_continuous_scale=["#00C851", "#FFBB33", "#FF4444"],
            range_color=[0, 0.30],
            text=df_contrib["Estresse (norm.)"].map(lambda x: f"{x:.0%}"),
        )
        fig_contrib.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ddd"),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickformat=".3f"),
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
            connector={"line": {"color": "rgba(255,255,255,0.2)"}},
            increasing={"marker": {"color": "#00C851"}},
            decreasing={"marker": {"color": "#FF4444"}},
            totals={"marker": {"color": cor_sim}},
        ))
        fig_wf.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ddd"),
            yaxis=dict(
                range=[0, 1100],
                gridcolor="rgba(255,255,255,0.08)",
                tickcolor="#aaa",
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
            return "color: #ff4444; font-weight:600"
        elif val < 0:
            return "color: #ff8800"
        elif val > 0:
            return "color: #00C851"
        return "color: #aaa"

    def colorir_rating(val):
        cores = {"A": "#00C851", "B": "#FFBB33", "C": "#FF8800", "D": "#FF4444"}
        c = cores.get(val, "#aaa")
        return f"color: {c}; font-weight:700"

    styled_df = (
        df_comp.style
        .applymap(colorir_delta, subset=["Δ Score"])
        .applymap(colorir_rating, subset=["Rating Base", "Rating Sim."])
        .format({
            "Score Base": "{:.0f}",
            "Score Simulado": "{:.0f}",
            "Δ Score": "{:+.0f}",
        })
    )

    st.dataframe(styled_df, use_container_width=True, hide_index=True)
