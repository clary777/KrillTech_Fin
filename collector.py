"""
collector.py — Módulo 1: Coletor & Parser de Dados Cadastrais
==============================================================
Responsabilidade: Receber um identificador de cliente (CNPJ) e retornar
um dicionário padronizado com dados cadastrais, societários e tempo de
atividade — o "dossiê" do cliente.

MOCK — Em produção, substituir `_buscar_dados_receita_federal()` por:
  - API Receita Federal / QSA (ex: ReceitaWS, BrasilAPI, Serpro DataValid)
  - APIs de bureaus de crédito (Serasa Experian, SPC Brasil)
  - APIs de dados judiciais (Escavador, DataJud CNJ)
  - API do SINTEGRA (situação fiscal estadual)
"""

from mock_data import CLIENTES


# ---------------------------------------------------------------------------
# FUNÇÃO PÚBLICA PRINCIPAL
# ---------------------------------------------------------------------------

def coletar_dados_cliente(cnpj: str) -> dict:
    """
    Ponto de entrada do módulo. Recebe um CNPJ e retorna o dossiê completo
    do cliente, já padronizado e enriquecido com campos derivados.

    Parâmetros:
        cnpj (str): CNPJ do cliente no formato '00.000.000/0001-00'

    Retorna:
        dict: Dicionário padronizado com dados cadastrais e indicadores
              derivados. Retorna dict vazio se o cliente não for encontrado.
    """
    dados_brutos = _buscar_dados_receita_federal(cnpj)
    if not dados_brutos:
        return {}

    dados_enriquecidos = _enriquecer_dados(dados_brutos)
    return dados_enriquecidos


# ---------------------------------------------------------------------------
# FUNÇÃO DE COLETA (MOCK)
# ---------------------------------------------------------------------------

def _buscar_dados_receita_federal(cnpj: str) -> dict:
    """
    MOCK — Substituir por chamada real à API da Receita Federal / QSA.

    Em produção, esta função faria:
        GET https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}
    e parsearia o retorno JSON para o formato interno padronizado.

    Por ora, retorna os dados diretamente do dicionário `mock_data.CLIENTES`.
    """
    return CLIENTES.get(cnpj, {})


# ---------------------------------------------------------------------------
# ENRIQUECIMENTO E DERIVAÇÕES
# ---------------------------------------------------------------------------

def _enriquecer_dados(dados: dict) -> dict:
    """
    Calcula campos derivados a partir dos dados brutos para uso nos módulos
    de scoring. Evita recalcular a mesma coisa em múltiplos módulos.
    """
    dados_enriquecidos = dados.copy()

    # --- Indicador de Alavancagem ---
    # Relação entre dívida total e faturamento anual.
    # Quanto mais próximo de 1 (ou acima), maior o risco de insolvência.
    fat = dados.get("faturamento_anual_brl", 1)
    div = dados.get("divida_total_brl", 0)
    dados_enriquecidos["alavancagem_ratio"] = round(div / fat, 4) if fat > 0 else 9.99

    # --- Tempo de Empresa (score de maturidade) ---
    # Empresas com mais de 15 anos recebem bônus de estabilidade.
    anos = dados.get("anos_atividade", 0)
    if anos >= 15:
        dados_enriquecidos["maturidade_score"] = 100
    elif anos >= 7:
        dados_enriquecidos["maturidade_score"] = 70
    elif anos >= 3:
        dados_enriquecidos["maturidade_score"] = 45
    else:
        dados_enriquecidos["maturidade_score"] = 20

    # --- Flag de Estrutura Societária Opaca ---
    # Sócios com CPF None geralmente indicam PJs ou fundos — maior due diligence.
    socios = dados.get("socios", [])
    dados_enriquecidos["estrutura_opaca"] = any(
        s.get("cpf") is None for s in socios
    )

    # --- Score Cadastral Composto (0–100) ---
    # Combina maturidade + fiscal + jurídico com pesos iguais como proxy
    # de saúde cadastral geral. Pesos podem ser calibrados com dados históricos.
    maturidade = dados_enriquecidos["maturidade_score"]
    fiscal = dados.get("score_fiscal_simulado", 50)
    juridico = dados.get("score_juridico_simulado", 50)
    dados_enriquecidos["score_cadastral"] = round(
        (maturidade * 0.25 + fiscal * 0.40 + juridico * 0.35), 2
    )

    return dados_enriquecidos


# ---------------------------------------------------------------------------
# HELPER: RESUMO TEXTUAL DO CLIENTE
# ---------------------------------------------------------------------------

def resumo_cadastral(dados: dict) -> str:
    """
    Gera uma string de resumo legível com as principais informações do cliente,
    usada no relatório final e na interface Streamlit.
    """
    if not dados:
        return "Cliente não encontrado."

    return (
        f"**{dados['razao_social']}** ({dados['cnpj']})\n"
        f"- Tipo: {dados['tipo']} | UF: {dados['uf']} — {dados['municipio']}\n"
        f"- Cultura Principal: {dados['cultura_principal']} | Área: {dados['area_ha']:,} ha\n"
        f"- Atividade: {dados['anos_atividade']} anos | "
        f"Faturamento: R$ {dados['faturamento_anual_brl']:,.0f}\n"
        f"- Dívida Total: R$ {dados['divida_total_brl']:,.0f} "
        f"(Alavancagem: {dados['alavancagem_ratio']:.1%})\n"
        f"- Score Cadastral Composto: {dados['score_cadastral']:.1f}/100"
    )
