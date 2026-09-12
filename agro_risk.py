"""
agro_risk.py — Módulo 2: Risco Agro & Climático
=================================================
Responsabilidade: Avaliar o risco específico da atividade agropecuária do
cliente com base em dados regionais de produtividade e risco climático.

MOCK — Em produção, substituir as tabelas fixas abaixo por chamadas reais a:
  - CONAB (Companhia Nacional de Abastecimento): séries históricas de produtividade
    por cultura e município.
  - INMET (Instituto Nacional de Meteorologia): risco climático regional.
  - MapBiomas / EMBRAPA: classificação de aptidão agrícola do solo.
  - ANA (Agência Nacional de Águas): disponibilidade hídrica.
"""

# ---------------------------------------------------------------------------
# TABELAS DE RISCO REGIONAL (MOCK)
# ---------------------------------------------------------------------------
# Score de 0 a 100 onde:
#   > 80 = baixo risco (alta produtividade, clima estável)
#   60-80 = risco moderado
#   40-60 = risco elevado
#   < 40  = risco crítico
# ---------------------------------------------------------------------------

# Risco climático por UF (média histórica simulada de volatilidade climática).
# Valores mais altos = menor risco climático (ambiente mais estável para o agro).
RISCO_CLIMATICO_UF = {
    "MT": 82,   # Centro-Oeste: clima previsível, alta produtividade
    "GO": 78,
    "MS": 75,
    "PR": 80,
    "RS": 68,   # Sul: geadas ocasionais reduzem o score
    "SP": 76,
    "MG": 72,
    "BA": 58,   # Nordeste: semiárido, risco de seca elevado
    "PI": 52,
    "MA": 65,
    "PA": 60,   # Norte: chuvas irregulares, logística difícil
    "AM": 55,
    "RO": 62,
    "TO": 63,
}

# Ajuste de produtividade por cultura (score parcial 0-100).
# Reflete a adequação regional de cada cultura e sua exposição a preços/clima.
PRODUTIVIDADE_CULTURA = {
    "Soja": 85,
    "Milho": 80,
    "Trigo": 72,
    "Algodão": 74,
    "Cana-de-Açúcar": 78,
    "Café": 76,
    "Pecuária Corte": 70,
    "Pecuária Leiteira": 68,
    "Dendê": 65,        # Alta dependência de clima equatorial
    "Arroz": 71,
    "Feijão": 65,
    "Mandioca": 62,
}

# Multiplicador regional de aptidão agronômica (por UF).
# Captura vantagens/desvantagens do solo e infraestrutura da região.
APTIDAO_REGIONAL = {
    "MT": 1.10,   # MATOPIBA + cerrado consolidado
    "GO": 1.05,
    "MS": 1.04,
    "PR": 1.08,   # Segundo maior produtor de grãos
    "RS": 1.02,
    "SP": 1.03,
    "MG": 0.97,
    "BA": 0.92,   # Oeste da Bahia tem boas áreas, mas logística desafia
    "PI": 0.88,
    "MA": 0.90,
    "PA": 0.85,   # Logística e regulação ambiental são gargalos
    "AM": 0.80,
    "RO": 0.83,
    "TO": 0.87,
}


# ---------------------------------------------------------------------------
# FUNÇÃO PÚBLICA PRINCIPAL
# ---------------------------------------------------------------------------

def calcular_score_agro(uf: str, cultura: str) -> dict:
    """
    Calcula o score agro-climático parcial do cliente (0–100).

    Lógica de composição:
        - 50% peso no risco climático da UF (estabilidade climática regional)
        - 35% peso na produtividade da cultura (histórico de rendimento)
        - 15% ajuste pelo multiplicador de aptidão regional

    Parâmetros:
        uf (str): Sigla da Unidade Federativa (ex: 'MT', 'RS')
        cultura (str): Nome da cultura principal (ex: 'Soja', 'Pecuária Corte')

    Retorna:
        dict com:
            score_agro (float): Score agro-climático parcial (0–100)
            risco_climatico (int): Score climático da UF
            produtividade_cultura (int): Score de produtividade da cultura
            aptidao_regional (float): Multiplicador de aptidão da UF
            detalhes (str): Texto explicativo para o relatório
    """
    risco_cli = RISCO_CLIMATICO_UF.get(uf, 65)  # default conservador
    prod_cult = PRODUTIVIDADE_CULTURA.get(cultura, 65)
    aptidao = APTIDAO_REGIONAL.get(uf, 0.90)

    # Score base: média ponderada de clima e produtividade
    score_base = (risco_cli * 0.50) + (prod_cult * 0.35)

    # Ajuste regional (multiplicador aplicado ao score base)
    # Limitamos o resultado ao intervalo [0, 100]
    score_agro = min(100.0, max(0.0, score_base * aptidao * (0.15 + 1)))
    # Nota: o `(0.15 + 1)` aqui serve para escalar o impacto do multiplicador
    # de aptidão de forma que diferenças pequenas (ex: 0.80 vs 1.10) se
    # traduzam em variações perceptíveis mas não dominantes no score final.

    # --- Recalculo simplificado e mais legível ---
    # score_agro = (risco_cli * 0.50 + prod_cult * 0.35) * aptidao + prod_cult * 0.15
    score_agro = round(
        (risco_cli * 0.50 + prod_cult * 0.35) * aptidao + prod_cult * 0.15,
        2
    )
    score_agro = min(100.0, max(0.0, score_agro))

    # Classificação qualitativa para o relatório
    if score_agro >= 80:
        classe = "Baixo Risco Agro-Climático"
    elif score_agro >= 65:
        classe = "Risco Agro-Climático Moderado"
    elif score_agro >= 50:
        classe = "Risco Agro-Climático Elevado"
    else:
        classe = "Risco Agro-Climático Crítico"

    detalhes = (
        f"UF {uf} — Score Climático: {risco_cli}/100 | "
        f"Cultura {cultura} — Produtividade: {prod_cult}/100 | "
        f"Aptidão Regional: {aptidao:.2f}x → **{classe}**"
    )

    return {
        "score_agro": score_agro,
        "risco_climatico": risco_cli,
        "produtividade_cultura": prod_cult,
        "aptidao_regional": aptidao,
        "classe_risco": classe,
        "detalhes": detalhes,
    }


# ---------------------------------------------------------------------------
# HELPER: Narrativa do Risco Agro
# ---------------------------------------------------------------------------

def narrativa_agro(uf: str, cultura: str, score_agro: float) -> str:
    """
    Gera uma frase curta para o relatório descrevendo o risco agro-climático.
    """
    apt = APTIDAO_REGIONAL.get(uf, 0.90)
    nivel = "favorável" if score_agro >= 70 else "moderado" if score_agro >= 55 else "desfavorável"
    return (
        f"O ambiente agro-climático em {uf} para a cultura de {cultura} é **{nivel}** "
        f"(score {score_agro:.1f}/100), com aptidão regional de {apt:.2f}x em relação à média nacional."
    )
