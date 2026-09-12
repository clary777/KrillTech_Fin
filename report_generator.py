"""
report_generator.py — Módulo 5: Sintetizador & Gerador de Relatório
=====================================================================
Responsabilidade: Receber os outputs de todos os módulos anteriores e
produzir um relatório estruturado em Markdown, pronto para renderização
no Streamlit.

O relatório inclui:
  - Cabeçalho de identificação do cliente
  - Score final com faixa de rating
  - Comparativo score idiossincrático vs. ajustado por macro
  - Detalhamento dos scores por dimensão
  - Lista de red flags com severidade
  - Contexto macroeconômico vigente
  - Recomendação operacional (limite e condições)
  - Resumo em linguagem natural (2-3 frases)
"""

from datetime import datetime


# ---------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# ---------------------------------------------------------------------------

def gerar_relatorio(
    dados_cliente: dict,
    resultado_agro: dict,
    resultado_macro: dict,
    resultado_scoring: dict,
) -> str:
    """
    Gera o relatório completo de risco de crédito em formato Markdown.

    Parâmetros:
        dados_cliente (dict): Output enriquecido do collector.py
        resultado_agro (dict): Output de agro_risk.calcular_score_agro()
        resultado_macro (dict): Output de macro_context.calcular_fator_estresse_macro()
        resultado_scoring (dict): Output de scoring_engine.calcular_score_final()

    Retorna:
        str: Relatório completo em Markdown
    """
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # ─── Seções do Relatório ─────────────────────────────────────────────────
    cabecalho       = _secao_cabecalho(dados_cliente, agora)
    scores_section  = _secao_scores(resultado_scoring)
    dimensoes       = _secao_dimensoes(resultado_scoring)
    macro_section   = _secao_macro(resultado_macro)
    red_flags_sec   = _secao_red_flags(resultado_scoring)
    recomendacao    = _secao_recomendacao(dados_cliente, resultado_scoring)
    resumo          = _gerar_resumo_linguagem_natural(
                          dados_cliente, resultado_scoring, resultado_macro
                      )
    rodape          = _secao_rodape()

    return "\n\n".join([
        cabecalho,
        scores_section,
        dimensoes,
        macro_section,
        red_flags_sec,
        recomendacao,
        resumo,
        rodape,
    ])


# ---------------------------------------------------------------------------
# SEÇÕES DO RELATÓRIO
# ---------------------------------------------------------------------------

def _secao_cabecalho(dados: dict, agora: str) -> str:
    alav = dados.get("alavancagem_ratio", 0)
    return f"""# 📋 Relatório de Risco de Crédito — KrillTech Fin
---
**Emitido em:** {agora} &nbsp;|&nbsp; **Analista:** Sistema KrillTech (Pipeline Automatizada)

## 🏢 Identificação do Cliente
| Campo | Valor |
|---|---|
| **Razão Social** | {dados.get('razao_social', '—')} |
| **CNPJ** | `{dados.get('cnpj', '—')}` |
| **Tipo** | {dados.get('tipo', '—')} |
| **Localização** | {dados.get('municipio', '—')}, {dados.get('uf', '—')} |
| **Cultura Principal** | {dados.get('cultura_principal', '—')} |
| **Área** | {dados.get('area_ha', 0):,} ha |
| **Anos de Atividade** | {dados.get('anos_atividade', 0)} anos |
| **Faturamento Anual** | R$ {dados.get('faturamento_anual_brl', 0):,.0f} |
| **Dívida Total** | R$ {dados.get('divida_total_brl', 0):,.0f} |
| **Alavancagem** | {alav:.1%} do faturamento |
| **Rating Histórico** | {dados.get('rating_historico', '—')} |"""


def _secao_scores(scoring: dict) -> str:
    score_idio  = scoring["score_idiossincrático"]
    score_adj   = scoring["score_ajustado"]
    variacao    = scoring["variacao_macro"]
    rating      = scoring["rating"]
    desc_rating = scoring["descricao_rating"]
    fator       = scoring["fator_estresse"]

    sinal = "▼" if variacao < 0 else "▲" if variacao > 0 else "►"
    cor_sinal = "vermelho" if variacao < 0 else "verde" if variacao > 0 else "neutro"

    return f"""---
## 📊 Score de Risco de Crédito

| Métrica | Valor |
|---|---|
| **Score Idiossincrático** (sem macro) | **{score_idio:.0f} / 1000** |
| **Score Ajustado por Macro** | **{score_adj:.0f} / 1000** |
| **Variação causada pelo macro** | {sinal} {abs(variacao):.0f} pontos |
| **Fator de Estresse Macro** | {fator:.3f}× |
| **Rating Final** | **{rating} — {desc_rating}** |"""


def _secao_dimensoes(scoring: dict) -> str:
    dimensoes = scoring.get("scores_dimensao", {})
    pesos     = scoring.get("pesos_dimensao", {})

    linhas = []
    chaves_map = {
        "Cadastral":       "cadastral",
        "Jurídico":        "juridico",
        "Fiscal":          "fiscal",
        "Agro-Climático":  "agro",
        "Financeiro":      "financeiro",
    }

    for nome_exib, chave_peso in chaves_map.items():
        score = dimensoes.get(nome_exib, 0)
        peso  = pesos.get(chave_peso, 0)
        barra = _barra_ascii(score)
        linhas.append(
            f"| {nome_exib} | {score:.0f}/100 | {peso:.0%} | {barra} |"
        )

    return f"""---
## 🔬 Composição do Score Idiossincrático

| Dimensão | Score | Peso | Visual |
|---|---|---|---|
{''.join(chr(10) + l for l in linhas)}"""


def _secao_macro(macro: dict) -> str:
    fator    = macro.get("fator_estresse", 1.0)
    interpret = macro.get("interpretacao", "")
    detalhes = macro.get("detalhes_por_variavel", {})

    linhas = []
    for chave, d in detalhes.items():
        stress_pct = f"{d['stress_normalizado']:.0%}"
        linhas.append(
            f"| {d['descricao']} | {d['valor']} {d['unidade']} "
            f"| {stress_pct} | {d['contribuicao_ponderada']:.4f} |"
        )

    return f"""---
## 🌐 Contexto Macroeconômico

**Fator de Estresse Macro:** `{fator:.4f}×` &nbsp;— {interpret}

| Variável | Valor Atual | Estresse Norm. | Contribuição |
|---|---|---|---|
{''.join(chr(10) + l for l in linhas)}"""


def _secao_red_flags(scoring: dict) -> str:
    flags = scoring.get("red_flags", [])

    if not flags:
        return """---
## 🚦 Red Flags

✅ **Nenhum red flag identificado.** O cliente apresenta perfil dentro dos parâmetros normais."""

    n_critico = sum(1 for f in flags if f["severidade"] == "CRÍTICO")
    n_alto    = sum(1 for f in flags if f["severidade"] == "ALTO")
    n_medio   = sum(1 for f in flags if f["severidade"] == "MÉDIO")

    linhas_flags = "\n".join(
        f"- **[{f['severidade']}]** `{f['codigo']}` — {f['mensagem']}"
        for f in flags
    )

    return f"""---
## 🚦 Red Flags Identificados

> **{len(flags)} alerta(s) detectado(s):** {n_critico} CRÍTICO(S) | {n_alto} ALTO(S) | {n_medio} MÉDIO(S)

{linhas_flags}"""


def _secao_recomendacao(dados: dict, scoring: dict) -> str:
    rating    = scoring["rating"]
    limite    = scoring["limite_credito_brl"]
    lim_pct   = scoring["limite_credito_pct"]
    condicoes = scoring["condicoes_pagamento"]
    tem_critico = scoring["tem_flag_critica"]

    if rating == "D" or tem_critico:
        decisao = "🔴 **CRÉDITO NEGADO**"
        justif  = "Score abaixo do mínimo operacional e/ou flags críticos ativos."
    elif rating == "C":
        decisao = "🟠 **CRÉDITO CONDICIONAL**"
        justif  = "Aprovação sujeita a aprovação da diretoria e reforço de garantias."
    elif rating == "B":
        decisao = "🟡 **CRÉDITO APROVADO COM RESTRIÇÕES**"
        justif  = "Aprovação dentro dos parâmetros normais com acompanhamento trimestral."
    else:
        decisao = "🟢 **CRÉDITO APROVADO**"
        justif  = "Cliente apresenta excelente perfil de risco. Aprovação automática."

    return f"""---
## 💼 Recomendação Operacional

**Decisão:** {decisao}
**Justificativa:** {justif}

| Parâmetro | Valor |
|---|---|
| **Limite de Crédito Sugerido** | R$ {limite:,.0f} ({lim_pct:.0%} do faturamento anual) |
| **Condições de Pagamento** | {condicoes} |
| **Próxima Revisão** | 90 dias (ou imediata se novo red flag) |"""


def _gerar_resumo_linguagem_natural(
    dados: dict,
    scoring: dict,
    macro: dict,
) -> str:
    """
    Gera um resumo de 2-3 frases em linguagem natural explicando o score.
    Em produção, esta função seria substituída por uma chamada a um LLM
    (ex: Gemini Pro via Vertex AI) para geração de narrativa mais sofisticada.
    Por ora, usa templates parametrizados.
    """
    nome         = dados.get("nome_fantasia", "O cliente")
    rating       = scoring["rating"]
    score_adj    = scoring["score_ajustado"]
    score_idio   = scoring["score_idiossincrático"]
    variacao     = scoring["variacao_macro"]
    fator        = macro.get("fator_estresse", 1.0)
    n_flags      = scoring["n_red_flags"]
    cultura      = dados.get("cultura_principal", "—")
    uf           = dados.get("uf", "—")

    # Frase 1: Perfil geral e score
    f1_map = {
        "A": f"**{nome}** apresenta excelente perfil de crédito (score {score_adj:.0f}/1000, rating A), "
             f"com sólida estrutura financeira e histórico operacional consistente.",
        "B": f"**{nome}** demonstra bom perfil de crédito (score {score_adj:.0f}/1000, rating B), "
             f"com fundamentos operacionais adequados e risco gerenciável.",
        "C": f"**{nome}** apresenta perfil de crédito regular (score {score_adj:.0f}/1000, rating C), "
             f"com vulnerabilidades financeiras e/ou operacionais que requerem atenção.",
        "D": f"**{nome}** apresenta perfil de crédito crítico (score {score_adj:.0f}/1000, rating D), "
             f"com múltiplos fatores de risco elevado que inviabilizam novas concessões.",
    }
    frase1 = f1_map.get(rating, f"Score: {score_adj:.0f}/1000.")

    # Frase 2: Impacto macro
    if abs(variacao) < 5:
        frase2 = (
            f"O ambiente macroeconômico atual (fator de estresse {fator:.3f}×) "
            f"tem impacto praticamente neutro sobre o score do cliente."
        )
    elif variacao < 0:
        frase2 = (
            f"O contexto macroeconômico adverso (fator de estresse {fator:.3f}×) "
            f"penalizou o score em {abs(variacao):.0f} pontos em relação ao score "
            f"idiossincrático de {score_idio:.0f}/1000, refletindo o encarecimento de "
            f"insumos e o custo do crédito na cadeia de {cultura}."
        )
    else:
        frase2 = (
            f"O ambiente macroeconômico favorável (fator {fator:.3f}×) "
            f"bonificou o score em {variacao:.0f} pontos acima do perfil intrínseco do cliente."
        )

    # Frase 3: Red flags e recomendação
    if n_flags == 0:
        frase3 = (
            f"Não foram identificados red flags — a operação pode seguir o fluxo "
            f"padrão de aprovação para clientes do segmento {dados.get('tipo','agro')} "
            f"em {uf}."
        )
    elif scoring["tem_flag_critica"]:
        frase3 = (
            f"Foram identificados {n_flags} red flag(s), incluindo alertas **CRÍTICOS** "
            f"que exigem bloqueio imediato de novas concessões e acionamento da área jurídica."
        )
    else:
        frase3 = (
            f"Foram identificados {n_flags} red flag(s) de severidade moderada a alta — "
            f"a aprovação requer validação adicional e reforço de garantias antes da liberação."
        )

    return f"""---
## 💬 Resumo Executivo

> {frase1}
>
> {frase2}
>
> {frase3}"""


def _secao_rodape() -> str:
    return """---
*Relatório gerado automaticamente pela Pipeline de Risco KrillTech Fin.
Este documento é de uso interno e não substitui análise humana em operações acima dos limites delegados.
Dados mockados para fins de demonstração — em produção, conectar às fontes listadas nos comentários dos módulos.*"""


# ---------------------------------------------------------------------------
# HELPER: barra ASCII de progresso (para tabelas Markdown)
# ---------------------------------------------------------------------------

def _barra_ascii(valor: float, largura: int = 20) -> str:
    """Gera uma barra de progresso em texto para uso em tabelas Markdown."""
    preenchido = int(round(valor / 100 * largura))
    vazio = largura - preenchido
    return f"`{'█' * preenchido}{'░' * vazio}` {valor:.0f}%"
