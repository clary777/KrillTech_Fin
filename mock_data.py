"""
mock_data.py — Dados Simulados de Clientes
===========================================
MOCK — Substituir por chamada real às APIs da Receita Federal (QSA),
Serasa, SINTEGRA e outros bureaus de dados quando em produção.

Os dados abaixo representam 7 clientes fictícios do agronegócio brasileiro,
construídos para cobrir diferentes perfis de risco (de A a D) e servir como
base de demonstração no pitch.
"""

# ---------------------------------------------------------------------------
# CLIENTES MOCKADOS
# ---------------------------------------------------------------------------
# Cada entry representa um produtor rural ou agroindústria fictício(a).
# Campos baseados no retorno típico de APIs de dados cadastrais / QSA.
# ---------------------------------------------------------------------------

CLIENTES = {
    "12.345.678/0001-90": {
        "cnpj": "12.345.678/0001-90",
        "razao_social": "Fazenda São Benedito Ltda.",
        "nome_fantasia": "Fazenda São Benedito",
        "tipo": "Produtor Rural PJ",
        "uf": "MT",
        "municipio": "Sorriso",
        "cultura_principal": "Soja",
        "cultura_secundaria": "Milho",
        "area_ha": 12_500,
        "anos_atividade": 18,
        "socios": [
            {"nome": "Roberto Alves Mendonça", "participacao_pct": 60, "cpf": "***.***.***-01"},
            {"nome": "Claudia Mendonça Pereira", "participacao_pct": 40, "cpf": "***.***.***-02"},
        ],
        "faturamento_anual_brl": 28_000_000,
        "divida_total_brl": 5_600_000,
        "limite_endividamento_contratual_brl": 14_000_000,  # 50% do faturamento
        "protestos": 0,
        "pedido_rj": False,
        "embargo_ambiental": False,
        "inadimplencia_tecnica": False,  # dívida < limite contratual
        "rating_historico": "A",
        "score_fiscal_simulado": 88,   # 0-100; simula compliance tributário
        "score_juridico_simulado": 92, # 0-100; simula ausência de processos
    },

    "98.765.432/0001-11": {
        "cnpj": "98.765.432/0001-11",
        "razao_social": "AgroSul Cereais S.A.",
        "nome_fantasia": "AgroSul Cereais",
        "tipo": "Agroindústria",
        "uf": "RS",
        "municipio": "Passo Fundo",
        "cultura_principal": "Trigo",
        "cultura_secundaria": "Soja",
        "area_ha": 45_000,
        "anos_atividade": 32,
        "socios": [
            {"nome": "Grupo AgroSul Holdings", "participacao_pct": 75, "cpf": None},
            {"nome": "Fundo Investimento Rural II", "participacao_pct": 25, "cpf": None},
        ],
        "faturamento_anual_brl": 95_000_000,
        "divida_total_brl": 22_000_000,
        "limite_endividamento_contratual_brl": 47_500_000,
        "protestos": 1,
        "pedido_rj": False,
        "embargo_ambiental": False,
        "inadimplencia_tecnica": False,
        "rating_historico": "B",
        "score_fiscal_simulado": 75,
        "score_juridico_simulado": 80,
    },

    "55.432.198/0001-33": {
        "cnpj": "55.432.198/0001-33",
        "razao_social": "Cerrado Verde Agropecuária Ltda.",
        "nome_fantasia": "Cerrado Verde",
        "tipo": "Produtor Rural PJ",
        "uf": "GO",
        "municipio": "Rio Verde",
        "cultura_principal": "Milho",
        "cultura_secundaria": "Pecuária Corte",
        "area_ha": 8_200,
        "anos_atividade": 9,
        "socios": [
            {"nome": "Paulo Sérgio Teixeira", "participacao_pct": 100, "cpf": "***.***.***-03"},
        ],
        "faturamento_anual_brl": 14_000_000,
        "divida_total_brl": 9_800_000,   # 70% do faturamento — próximo do limite
        "limite_endividamento_contratual_brl": 7_000_000,  # 50% do faturamento
        "protestos": 3,
        "pedido_rj": False,
        "embargo_ambiental": False,
        "inadimplencia_tecnica": True,   # dívida > limite contratual
        "rating_historico": "C",
        "score_fiscal_simulado": 55,
        "score_juridico_simulado": 60,
    },

    "77.001.234/0001-55": {
        "cnpj": "77.001.234/0001-55",
        "razao_social": "NordAgro Irrigação S.A.",
        "nome_fantasia": "NordAgro",
        "tipo": "Produtor Rural PJ",
        "uf": "BA",
        "municipio": "Barreiras",
        "cultura_principal": "Algodão",
        "cultura_secundaria": "Soja",
        "area_ha": 22_000,
        "anos_atividade": 14,
        "socios": [
            {"nome": "Família Holanda Neto (Holding)", "participacao_pct": 55, "cpf": None},
            {"nome": "BancoCoop Investimentos", "participacao_pct": 45, "cpf": None},
        ],
        "faturamento_anual_brl": 41_000_000,
        "divida_total_brl": 11_000_000,
        "limite_endividamento_contratual_brl": 20_500_000,
        "protestos": 0,
        "pedido_rj": False,
        "embargo_ambiental": True,   # embargo ambiental simulado (IBAMA)
        "inadimplencia_tecnica": False,
        "rating_historico": "B",
        "score_fiscal_simulado": 70,
        "score_juridico_simulado": 65,
    },

    "33.987.654/0001-22": {
        "cnpj": "33.987.654/0001-22",
        "razao_social": "Pantanal Pecuária & Grãos Ltda.",
        "nome_fantasia": "Pantanal P&G",
        "tipo": "Produtor Rural PJ",
        "uf": "MS",
        "municipio": "Corumbá",
        "cultura_principal": "Pecuária Corte",
        "cultura_secundaria": "Soja",
        "area_ha": 31_000,
        "anos_atividade": 25,
        "socios": [
            {"nome": "José Ronaldo Meireles", "participacao_pct": 70, "cpf": "***.***.***-04"},
            {"nome": "Ana Beatriz Meireles", "participacao_pct": 30, "cpf": "***.***.***-05"},
        ],
        "faturamento_anual_brl": 52_000_000,
        "divida_total_brl": 8_500_000,
        "limite_endividamento_contratual_brl": 26_000_000,
        "protestos": 0,
        "pedido_rj": False,
        "embargo_ambiental": False,
        "inadimplencia_tecnica": False,
        "rating_historico": "A",
        "score_fiscal_simulado": 85,
        "score_juridico_simulado": 88,
    },

    "19.876.543/0001-77": {
        "cnpj": "19.876.543/0001-77",
        "razao_social": "Amazônia Agroflorestal S.A.",
        "nome_fantasia": "AmazonAgro",
        "tipo": "Agroindústria",
        "uf": "PA",
        "municipio": "Santarém",
        "cultura_principal": "Dendê",
        "cultura_secundaria": "Soja",
        "area_ha": 18_500,
        "anos_atividade": 7,
        "socios": [
            {"nome": "Green Capital Fund LLC", "participacao_pct": 60, "cpf": None},
            {"nome": "Carlos Drummond Vilela", "participacao_pct": 40, "cpf": "***.***.***-06"},
        ],
        "faturamento_anual_brl": 22_000_000,
        "divida_total_brl": 18_000_000,  # 82% do faturamento — alto
        "limite_endividamento_contratual_brl": 11_000_000,
        "protestos": 6,
        "pedido_rj": True,   # pedido de recuperação judicial simulado
        "embargo_ambiental": True,
        "inadimplencia_tecnica": True,
        "rating_historico": "D",
        "score_fiscal_simulado": 30,
        "score_juridico_simulado": 20,
    },

    "44.321.987/0001-66": {
        "cnpj": "44.321.987/0001-66",
        "razao_social": "TriAgro Cooperativa de Produção",
        "nome_fantasia": "TriAgro Coop",
        "tipo": "Cooperativa",
        "uf": "PR",
        "municipio": "Londrina",
        "cultura_principal": "Soja",
        "cultura_secundaria": "Café",
        "area_ha": 67_000,
        "anos_atividade": 41,
        "socios": [
            {"nome": "Cooperados (3.200 membros)", "participacao_pct": 100, "cpf": None},
        ],
        "faturamento_anual_brl": 180_000_000,
        "divida_total_brl": 35_000_000,
        "limite_endividamento_contratual_brl": 90_000_000,
        "protestos": 0,
        "pedido_rj": False,
        "embargo_ambiental": False,
        "inadimplencia_tecnica": False,
        "rating_historico": "A",
        "score_fiscal_simulado": 90,
        "score_juridico_simulado": 95,
    },
}

# Acesso por lista ordenada (para o dropdown do Streamlit)
LISTA_CLIENTES = [
    f"{v['cnpj']} — {v['nome_fantasia']}"
    for v in CLIENTES.values()
]


def get_cliente(cnpj: str) -> dict:
    """Retorna dados mockados do cliente pelo CNPJ."""
    return CLIENTES.get(cnpj, {})


# ---------------------------------------------------------------------------
# DADOS SIMULADOS — OPEN FINANCE (DEMONSTRAÇÃO)
# ---------------------------------------------------------------------------
# Simula dados que seriam obtidos via APIs de Open Finance (Open Banking Brasil)
# do Banco Central, com consentimento do cliente. Inclui:
#   - Saldos e movimentação de contas
#   - Operações de crédito ativas
#   - Histórico de pagamentos
#   - Indicadores de saúde financeira
#
# MOCK — Em produção, substituir por chamadas às APIs do ecossistema Open Finance:
#   - /accounts (saldos e extratos)
#   - /credit-operations (operações de crédito)
#   - /financings (financiamentos)
#   - /invoice-financings (desconto de duplicatas)
# ---------------------------------------------------------------------------

OPEN_FINANCE = {
    # ── Fazenda São Benedito — Rating A, saúde excelente ──────────────────
    "12.345.678/0001-90": {
        "consentimento_ativo": True,
        "instituicoes_conectadas": ["Banco do Brasil", "Sicoob"],
        "saldo_conta_corrente_brl": 2_840_000,
        "saldo_3_meses_atras_brl": 2_120_000,
        "tendencia_saldo": "crescente",
        "receita_media_mensal_brl": 2_333_000,
        "despesa_media_mensal_brl": 1_680_000,
        "operacoes_credito_ativas": 2,
        "valor_total_divida_brl": 4_200_000,
        "parcelas_em_dia": 24,
        "parcelas_atrasadas_30d": 0,
        "parcelas_atrasadas_60d": 0,
        "parcelas_atrasadas_90d": 0,
        "limite_credito_total_brl": 8_000_000,
        "limite_utilizado_brl": 4_200_000,
        "utilizacao_credito_pct": 52.5,
        "comprometimento_renda_pct": 18.2,
        "indice_cobertura_divida": 3.12,  # receita / parcela mensal
        "score_pontualidade": 98,  # 0–100
        "qtd_instituicoes_com_divida": 1,
        "cheque_devolvido_12m": 0,
        "protestos_12m": 0,
        "risco_inadimplencia": "BAIXO",
        "alerta_inadimplencia": False,
        "meses_ate_risco_estimado": None,
        "observacao": "Fluxo de caixa sólido. Endividamento controlado.",
    },

    # ── AgroSul Cereais — Rating A, 1 flag (protesto) ────────────────────
    "98.765.432/0001-11": {
        "consentimento_ativo": True,
        "instituicoes_conectadas": ["Banrisul", "Banco do Brasil", "Bradesco"],
        "saldo_conta_corrente_brl": 5_400_000,
        "saldo_3_meses_atras_brl": 6_100_000,
        "tendencia_saldo": "leve_queda",
        "receita_media_mensal_brl": 7_916_000,
        "despesa_media_mensal_brl": 6_800_000,
        "operacoes_credito_ativas": 5,
        "valor_total_divida_brl": 18_500_000,
        "parcelas_em_dia": 58,
        "parcelas_atrasadas_30d": 1,
        "parcelas_atrasadas_60d": 0,
        "parcelas_atrasadas_90d": 0,
        "limite_credito_total_brl": 32_000_000,
        "limite_utilizado_brl": 18_500_000,
        "utilizacao_credito_pct": 57.8,
        "comprometimento_renda_pct": 24.1,
        "indice_cobertura_divida": 2.48,
        "score_pontualidade": 91,
        "qtd_instituicoes_com_divida": 3,
        "cheque_devolvido_12m": 0,
        "protestos_12m": 1,
        "risco_inadimplencia": "BAIXO",
        "alerta_inadimplencia": False,
        "meses_ate_risco_estimado": None,
        "observacao": "Saldo em queda leve e 1 protesto registrado. Monitorar.",
    },

    # ── Cerrado Verde — Rating B, 2 flags ────────────────────────────────
    "55.432.198/0001-33": {
        "consentimento_ativo": True,
        "instituicoes_conectadas": ["Banco do Brasil", "Sicredi"],
        "saldo_conta_corrente_brl": 380_000,
        "saldo_3_meses_atras_brl": 920_000,
        "tendencia_saldo": "queda_acentuada",
        "receita_media_mensal_brl": 1_166_000,
        "despesa_media_mensal_brl": 1_090_000,
        "operacoes_credito_ativas": 4,
        "valor_total_divida_brl": 9_800_000,
        "parcelas_em_dia": 18,
        "parcelas_atrasadas_30d": 3,
        "parcelas_atrasadas_60d": 1,
        "parcelas_atrasadas_90d": 0,
        "limite_credito_total_brl": 10_000_000,
        "limite_utilizado_brl": 9_800_000,
        "utilizacao_credito_pct": 98.0,
        "comprometimento_renda_pct": 62.4,
        "indice_cobertura_divida": 1.07,
        "score_pontualidade": 64,
        "qtd_instituicoes_com_divida": 2,
        "cheque_devolvido_12m": 2,
        "protestos_12m": 1,
        "risco_inadimplencia": "ELEVADO",
        "alerta_inadimplencia": True,
        "meses_ate_risco_estimado": 4,
        "observacao": "Saldo caiu 59% em 3 meses. Utilização de crédito em 98%. Capacidade de pagamento no limite.",
    },

    # ── NordAgro — Rating B, 1 flag ──────────────────────────────────────
    "77.001.234/0001-55": {
        "consentimento_ativo": True,
        "instituicoes_conectadas": ["BNB", "Banco do Brasil"],
        "saldo_conta_corrente_brl": 1_200_000,
        "saldo_3_meses_atras_brl": 1_450_000,
        "tendencia_saldo": "leve_queda",
        "receita_media_mensal_brl": 3_416_000,
        "despesa_media_mensal_brl": 2_950_000,
        "operacoes_credito_ativas": 3,
        "valor_total_divida_brl": 8_200_000,
        "parcelas_em_dia": 32,
        "parcelas_atrasadas_30d": 2,
        "parcelas_atrasadas_60d": 0,
        "parcelas_atrasadas_90d": 0,
        "limite_credito_total_brl": 14_000_000,
        "limite_utilizado_brl": 8_200_000,
        "utilizacao_credito_pct": 58.6,
        "comprometimento_renda_pct": 38.7,
        "indice_cobertura_divida": 1.68,
        "score_pontualidade": 78,
        "qtd_instituicoes_com_divida": 2,
        "cheque_devolvido_12m": 0,
        "protestos_12m": 0,
        "risco_inadimplencia": "MODERADO",
        "alerta_inadimplencia": False,
        "meses_ate_risco_estimado": 9,
        "observacao": "Comprometimento de renda acima de 35%. Tendência de queda no saldo.",
    },

    # ── Pantanal P&G — Rating A, sem flags ───────────────────────────────
    "33.987.654/0001-22": {
        "consentimento_ativo": True,
        "instituicoes_conectadas": ["Banco do Brasil", "Bradesco", "Itaú"],
        "saldo_conta_corrente_brl": 4_600_000,
        "saldo_3_meses_atras_brl": 3_900_000,
        "tendencia_saldo": "crescente",
        "receita_media_mensal_brl": 4_333_000,
        "despesa_media_mensal_brl": 3_100_000,
        "operacoes_credito_ativas": 3,
        "valor_total_divida_brl": 10_400_000,
        "parcelas_em_dia": 36,
        "parcelas_atrasadas_30d": 0,
        "parcelas_atrasadas_60d": 0,
        "parcelas_atrasadas_90d": 0,
        "limite_credito_total_brl": 22_000_000,
        "limite_utilizado_brl": 10_400_000,
        "utilizacao_credito_pct": 47.3,
        "comprometimento_renda_pct": 21.5,
        "indice_cobertura_divida": 2.84,
        "score_pontualidade": 100,
        "qtd_instituicoes_com_divida": 2,
        "cheque_devolvido_12m": 0,
        "protestos_12m": 0,
        "risco_inadimplencia": "BAIXO",
        "alerta_inadimplencia": False,
        "meses_ate_risco_estimado": None,
        "observacao": "Excelente saúde financeira. Pontualidade perfeita.",
    },

    # ── AmazonAgro — Rating D, 4 flags, PERTO DA INADIMPLÊNCIA ──────────
    "19.876.543/0001-77": {
        "consentimento_ativo": True,
        "instituicoes_conectadas": ["Banco da Amazônia", "Banco do Brasil"],
        "saldo_conta_corrente_brl": 42_000,
        "saldo_3_meses_atras_brl": 1_350_000,
        "tendencia_saldo": "colapso",
        "receita_media_mensal_brl": 1_833_000,
        "despesa_media_mensal_brl": 2_100_000,
        "operacoes_credito_ativas": 6,
        "valor_total_divida_brl": 18_000_000,
        "parcelas_em_dia": 8,
        "parcelas_atrasadas_30d": 5,
        "parcelas_atrasadas_60d": 4,
        "parcelas_atrasadas_90d": 2,
        "limite_credito_total_brl": 18_500_000,
        "limite_utilizado_brl": 18_000_000,
        "utilizacao_credito_pct": 97.3,
        "comprometimento_renda_pct": 89.4,
        "indice_cobertura_divida": 0.54,
        "score_pontualidade": 22,
        "qtd_instituicoes_com_divida": 2,
        "cheque_devolvido_12m": 7,
        "protestos_12m": 4,
        "risco_inadimplencia": "CRÍTICO",
        "alerta_inadimplencia": True,
        "meses_ate_risco_estimado": 1,
        "observacao": "Despesas superam receitas. Saldo caiu 97% em 3 meses. "
                      "11 parcelas atrasadas. Cobertura de dívida abaixo de 1. "
                      "Inadimplência iminente.",
    },

    # ── TriAgro Coop — Rating A, sem flags ───────────────────────────────
    "44.321.987/0001-66": {
        "consentimento_ativo": True,
        "instituicoes_conectadas": ["Sicredi", "Banco do Brasil", "Cresol", "Bradesco"],
        "saldo_conta_corrente_brl": 18_200_000,
        "saldo_3_meses_atras_brl": 15_800_000,
        "tendencia_saldo": "crescente",
        "receita_media_mensal_brl": 15_000_000,
        "despesa_media_mensal_brl": 11_200_000,
        "operacoes_credito_ativas": 8,
        "valor_total_divida_brl": 36_000_000,
        "parcelas_em_dia": 96,
        "parcelas_atrasadas_30d": 0,
        "parcelas_atrasadas_60d": 0,
        "parcelas_atrasadas_90d": 0,
        "limite_credito_total_brl": 80_000_000,
        "limite_utilizado_brl": 36_000_000,
        "utilizacao_credito_pct": 45.0,
        "comprometimento_renda_pct": 16.8,
        "indice_cobertura_divida": 3.57,
        "score_pontualidade": 100,
        "qtd_instituicoes_com_divida": 3,
        "cheque_devolvido_12m": 0,
        "protestos_12m": 0,
        "risco_inadimplencia": "BAIXO",
        "alerta_inadimplencia": False,
        "meses_ate_risco_estimado": None,
        "observacao": "Cooperativa de grande porte com saúde financeira robusta.",
    },
}
