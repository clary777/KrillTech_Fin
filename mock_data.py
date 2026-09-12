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
