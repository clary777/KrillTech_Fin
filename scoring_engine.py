"""
scoring_engine.py — Módulo 4: Motor de Decisão & Scoring
==========================================================
Responsabilidade: Calcular o score final de risco de crédito (0–1000),
combinando os scores idiossincráticos do cliente com o fator de estresse
macroeconômico do módulo macro_context.

ARQUITETURA DO SCORE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score Idiossincrático (0–1000)
   └─ Score Cadastral         → peso 25%  (maturidade, fiscal, jurídico)
   └─ Score Jurídico/Processual → peso 20%  (processos, protestos)
   └─ Score Fiscal            → peso 20%  (compliance tributário simulado)
   └─ Score Agro-Climático    → peso 20%  (região, cultura, clima)
   └─ Score Financeiro        → peso 15%  (alavancagem, capacidade de pagamento)

Score Ajustado = Score Idiossincrático × (2 - fator_estresse)
   → fator_estresse > 1.0 → penaliza
   → fator_estresse < 1.0 → bonifica (teto: não ultrapassa 1000)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PESOS DO SCORE IDIOSSINCRÁTICO:
  - Cadastral (maturidade + fiscal + jurídico): 25%
  - Jurídico/Processual (protestos, RJ, embargo): 20%
  - Fiscal (compliance tributário): 20%
  - Agro-Climático (região + cultura): 20%
  - Financeiro (alavancagem + endividamento): 15%
"""

# ---------------------------------------------------------------------------
# CONSTANTES DE PESO (devem somar 1.0)
# ---------------------------------------------------------------------------
PESOS = {
    "cadastral": 0.25,
    "juridico": 0.20,
    "fiscal": 0.20,
    "agro": 0.20,
    "financeiro": 0.15,
}

# Faixas de rating — baseadas no score ajustado final (0–1000)
FAIXAS_RATING = [
    (800, 1000, "A", "Excelente — Risco Mínimo"),
    (600, 799,  "B", "Bom — Risco Baixo a Moderado"),
    (400, 599,  "C", "Regular — Risco Elevado"),
    (0,   399,  "D", "Crítico — Risco Muito Alto"),
]

# Limites de crédito sugeridos por faixa (% do faturamento anual)
LIMITE_CREDITO_PCT = {
    "A": 0.40,   # até 40% do faturamento
    "B": 0.25,
    "C": 0.10,
    "D": 0.00,   # negar crédito
}

# Condições de pagamento sugeridas por faixa
CONDICOES_PAGAMENTO = {
    "A": "Prazo de até 36 meses, carência de 12 meses, taxa referenciada ao CDI + 1,5% a.a.",
    "B": "Prazo de até 24 meses, carência de 6 meses, taxa CDI + 3,5% a.a. com garantias reais.",
    "C": "Prazo de até 12 meses, sem carência, taxa CDI + 6,0% a.a. com aval + hipoteca da área.",
    "D": "Crédito negado. Renegociar exposições existentes e acionar garantias.",
}


# ---------------------------------------------------------------------------
# SCORE JURÍDICO/PROCESSUAL (sub-componente)
# ---------------------------------------------------------------------------

def _calcular_score_juridico(dados_cliente: dict) -> float:
    """
    Calcula o score jurídico/processual (0–100) com base em eventos
    negativos simulados: pedido de RJ, embargo ambiental e protestos.

    Partimos do score bruto do cliente e aplicamos penalizações:
      - Pedido de RJ: -50 pontos (evento gravíssimo)
      - Embargo ambiental: -25 pontos (risco regulatório severo)
      - Cada protesto: -5 pontos (até no máximo -30)
    """
    score = dados_cliente.get("score_juridico_simulado", 50)

    if dados_cliente.get("pedido_rj", False):
        score -= 50   # RJ é evento de crédito crítico

    if dados_cliente.get("embargo_ambiental", False):
        score -= 25   # Risco regulatório severo — pode impedir operações

    protestos = dados_cliente.get("protestos", 0)
    penalidade_protestos = min(30, protestos * 5)  # teto de -30 pts
    score -= penalidade_protestos

    return max(0.0, min(100.0, float(score)))


# ---------------------------------------------------------------------------
# SCORE FINANCEIRO (sub-componente)
# ---------------------------------------------------------------------------

def _calcular_score_financeiro(dados_cliente: dict) -> float:
    """
    Calcula o score financeiro (0–100) com base na alavancagem e
    na situação de inadimplência técnica.

    Lógica:
      - Alavancagem ≤ 30%  → score base 100
      - Alavancagem 30–50% → score base 75
      - Alavancagem 50–70% → score base 50
      - Alavancagem > 70%  → score base 25
      - Inadimplência técnica: -30 pontos adicionais
    """
    alavancagem = dados_cliente.get("alavancagem_ratio", 0.5)

    if alavancagem <= 0.30:
        score = 100.0
    elif alavancagem <= 0.50:
        score = 75.0
    elif alavancagem <= 0.70:
        score = 50.0
    else:
        score = 25.0

    if dados_cliente.get("inadimplencia_tecnica", False):
        score -= 30.0   # Violação de covenant contratual

    return max(0.0, min(100.0, score))


# ---------------------------------------------------------------------------
# RED FLAGS
# ---------------------------------------------------------------------------

def detectar_red_flags(dados_cliente: dict, resultado_macro: dict) -> list[dict]:
    """
    Detecta red flags (alertas de risco) com base nos dados do cliente e
    no contexto macroeconômico.

    Retorna uma lista de dicionários, cada um com:
        - codigo (str): identificador do red flag
        - severidade (str): 'CRÍTICO', 'ALTO', 'MÉDIO'
        - mensagem (str): descrição do alerta para o relatório
    """
    flags = []

    # --- RJ: Recuperação Judicial ---
    if dados_cliente.get("pedido_rj", False):
        flags.append({
            "codigo": "RJ_ATIVO",
            "severidade": "CRÍTICO",
            "mensagem": "⛔ Pedido de Recuperação Judicial ativo — evento de crédito crítico. "
                        "Suspender novas concessões imediatamente.",
        })

    # --- Embargo Ambiental ---
    if dados_cliente.get("embargo_ambiental", False):
        flags.append({
            "codigo": "EMBARGO_AMBIENTAL",
            "severidade": "ALTO",
            "mensagem": "🚫 Embargo ambiental identificado (IBAMA/órgão estadual). "
                        "Risco operacional e regulatório elevado — pode impedir a colheita.",
        })

    # --- Protestos acima do limiar ---
    protestos = dados_cliente.get("protestos", 0)
    if protestos >= 3:
        flags.append({
            "codigo": "PROTESTOS_ELEVADOS",
            "severidade": "ALTO",
            "mensagem": f"⚠️ {protestos} protestos registrados — indica dificuldade recorrente "
                        f"de pagamento. Limiar de alerta: ≥ 3 protestos.",
        })
    elif protestos >= 1:
        flags.append({
            "codigo": "PROTESTOS_MODERADOS",
            "severidade": "MÉDIO",
            "mensagem": f"🔔 {protestos} protesto(s) registrado(s) — monitorar evolução.",
        })

    # --- Inadimplência Técnica (covenant breach) ---
    if dados_cliente.get("inadimplencia_tecnica", False):
        fat = dados_cliente.get("faturamento_anual_brl", 1)
        div = dados_cliente.get("divida_total_brl", 0)
        lim = dados_cliente.get("limite_endividamento_contratual_brl", 0)
        flags.append({
            "codigo": "INADIMPLENCIA_TECNICA",
            "severidade": "CRÍTICO",
            "mensagem": f"⛔ Inadimplência técnica: dívida total (R$ {div:,.0f}) excede o limite "
                        f"contratual (R$ {lim:,.0f}, = 50% do faturamento de R$ {fat:,.0f}). "
                        f"Violação de covenant — acionar cláusula de vencimento antecipado.",
        })

    # --- Exposição a Choque Macro ---
    if resultado_macro.get("acima_do_limiar", False):
        fator = resultado_macro.get("fator_estresse", 1.0)
        flags.append({
            "codigo": "CHOQUE_MACRO",
            "severidade": "ALTO",
            "mensagem": f"🌐 Exposição setorial a choque macroeconômico: fator de estresse = "
                        f"{fator:.3f} (limiar de alerta: ≥ 1.10). O custo de produção "
                        f"do setor deve ser reavaliado antes da liberação de crédito.",
        })

    # --- Alavancagem muito alta (sem violação de covenant) ---
    alav = dados_cliente.get("alavancagem_ratio", 0)
    if alav > 0.70 and not dados_cliente.get("inadimplencia_tecnica", False):
        flags.append({
            "codigo": "ALAVANCAGEM_ALTA",
            "severidade": "MÉDIO",
            "mensagem": f"🔔 Alavancagem elevada: dívida representa {alav:.1%} do faturamento anual. "
                        f"Monitorar capacidade de geração de caixa nas próximas safras.",
        })

    return flags


# ---------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE SCORING
# ---------------------------------------------------------------------------

def calcular_score_final(
    dados_cliente: dict,
    resultado_agro: dict,
    resultado_macro: dict,
) -> dict:
    """
    Calcula o score final de risco de crédito (0–1000) e retorna todos os
    componentes separados para exibição no relatório.

    Parâmetros:
        dados_cliente (dict): Retorno enriquecido do collector.py
        resultado_agro (dict): Retorno de agro_risk.calcular_score_agro()
        resultado_macro (dict): Retorno de macro_context.calcular_fator_estresse_macro()

    Retorna:
        dict com todos os scores, rating, red flags e recomendação.
    """

    # --- 1. Scores por dimensão (todos em 0–100) ---
    s_cadastral  = dados_cliente.get("score_cadastral", 50.0)
    s_juridico   = _calcular_score_juridico(dados_cliente)
    s_fiscal     = float(dados_cliente.get("score_fiscal_simulado", 50))
    s_agro       = resultado_agro.get("score_agro", 50.0)
    s_financeiro = _calcular_score_financeiro(dados_cliente)

    # --- 2. Score Idiossincrático (0–100) como média ponderada ---
    score_idio_100 = (
        s_cadastral  * PESOS["cadastral"]  +
        s_juridico   * PESOS["juridico"]   +
        s_fiscal     * PESOS["fiscal"]     +
        s_agro       * PESOS["agro"]       +
        s_financeiro * PESOS["financeiro"]
    )

    # Converter para escala 0–1000
    score_idio = round(score_idio_100 * 10, 1)

       # --- 3. Score Ajustado por Macro ---
    # Ambiente ADVERSO (fator >= 1.0): penalidade multiplicativa direta.
    #   score_ajustado = score_idio × (2 - fator_estresse)
    #   fator = 1.0 → neutro (×1.0) | fator = 1.3 → penaliza (×0.7)
    #
    # Ambiente FAVORÁVEL (fator < 1.0): bônus proporcional ao espaço
    # restante até 1000 (headroom), em vez de multiplicar direto.
    # Isso evita que clientes com score idiossincrático já alto estourem
    # o teto de 1000 e percam diferenciação entre si (bug identificado:
    # 3 de 7 clientes mockados batiam exatamente em 1000).
    #   score_ajustado = score_idio + (1000 - score_idio) × (1 - fator)
    fator = resultado_macro.get("fator_estresse", 1.0)

    if fator >= 1.0:
        multiplicador_ajuste = 2.0 - fator
        score_ajustado = score_idio * multiplicador_ajuste
    else:
        multiplicador_ajuste = None  # não se aplica no ramo favorável (bônus por headroom)
        score_ajustado = score_idio + (1000.0 - score_idio) * (1.0 - fator)

    score_ajustado = round(min(1000.0, max(0.0, score_ajustado)), 1)

    # Multiplicador efetivo (para exibição), calculado a posteriori em
    # ambos os ramos — mantém compatibilidade com quem consome esse campo.
    multiplicador_ajuste = round(score_ajustado / score_idio, 4) if score_idio > 0 else 1.0
    # --- 4. Variação causada pelo macro ---
    variacao_macro = round(score_ajustado - score_idio, 1)

    # --- 5. Faixa de Rating ---
    rating, descricao_rating = "D", "Crítico — Risco Muito Alto"
    for score_min, score_max, faixa, desc in FAIXAS_RATING:
        if score_min <= score_ajustado <= score_max:
            rating = faixa
            descricao_rating = desc
            break

    # --- 6. Red Flags ---
    red_flags = detectar_red_flags(dados_cliente, resultado_macro)

    # --- 7. Recomendação Operacional ---
    faturamento = dados_cliente.get("faturamento_anual_brl", 0)
    limite_pct  = LIMITE_CREDITO_PCT.get(rating, 0)
    limite_brl  = round(faturamento * limite_pct, -3)  # arredonda p/ milhares
    condicoes   = CONDICOES_PAGAMENTO.get(rating, "Consultar diretoria de crédito.")

    return {
        # --- Scores por dimensão ---
        "scores_dimensao": {
            "Cadastral":   round(s_cadastral, 1),
            "Jurídico":    round(s_juridico, 1),
            "Fiscal":      round(s_fiscal, 1),
            "Agro-Climático": round(s_agro, 1),
            "Financeiro":  round(s_financeiro, 1),
        },
        "pesos_dimensao": PESOS,

        # --- Scores finais ---
        "score_idiossincrático": score_idio,
        "score_ajustado":        score_ajustado,
        "variacao_macro":        variacao_macro,
        "multiplicador_ajuste":  round(multiplicador_ajuste, 4),
        "fator_estresse":        fator,

        # --- Rating e recomendação ---
        "rating":          rating,
        "descricao_rating": descricao_rating,
        "limite_credito_brl": limite_brl,
        "limite_credito_pct": limite_pct,
        "condicoes_pagamento": condicoes,

        # --- Red Flags ---
        "red_flags": red_flags,
        "n_red_flags": len(red_flags),
        "tem_flag_critica": any(f["severidade"] == "CRÍTICO" for f in red_flags),
    }


# ---------------------------------------------------------------------------
# HELPER: Cor da faixa de rating (para Streamlit)
# ---------------------------------------------------------------------------

CORES_RATING = {
    "A": "#00C851",   # verde
    "B": "#FFBB33",   # amarelo
    "C": "#FF8800",   # laranja
    "D": "#FF4444",   # vermelho
}

def cor_rating(rating: str) -> str:
    return CORES_RATING.get(rating, "#888888")
