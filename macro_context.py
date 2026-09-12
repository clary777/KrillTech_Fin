"""
macro_context.py — Módulo 3: Contexto Macroeconômico
======================================================
Responsabilidade: Modelar o ambiente macroeconômico e calcular um fator de
estresse que é aplicado como multiplicador sobre o score base do cliente.

Lógica central:
  - Cada variável macro é normalizada para uma escala 0–1 (onde 1 = máximo estresse).
  - O fator de estresse resultante é uma média ponderada das variáveis normalizadas,
    mapeada para o intervalo [0.75, 1.30] via transformação linear.
  - Fator > 1.0 = ambiente desfavorável → penaliza o score final.
  - Fator < 1.0 = ambiente favorável → bonifica o score final.

MOCK — Em produção, substituir `obter_variaveis_macro_atuais()` por:
  - Câmbio: API do Banco Central do Brasil (BCB SGS série 1)
  - Petróleo: API Alpha Vantage, Yahoo Finance ou Quandl (série Brent ICE)
  - Fertilizantes: World Bank Commodity Price Data (Pink Sheet) ou CRU Group
  - Selic: BCB SGS série 432 (taxa Selic Over)
  - Risco Geopolítico: GPR Index (Caldara & Iacoviello), via download CSV ou API
"""

# ---------------------------------------------------------------------------
# VARIÁVEIS MACRO — REFERÊNCIAS E LIMITES DE NORMALIZAÇÃO
# ---------------------------------------------------------------------------
# Para cada variável definimos (valor_referencia, valor_estresse_max):
#   - valor_referencia: o nível "neutro" (estresse = 0)
#   - valor_estresse_max: o nível de máximo estresse (estresse = 1)
# Qualquer valor abaixo de referência é tratado como estresse = 0 (não há
# bônus extra por ambiente muito favorável — tratamos assimetricamente para
# conservadorismo).
# ---------------------------------------------------------------------------

PARAMETROS_MACRO = {
    # Câmbio USD/BRL: referência 5.0; estresse máximo = 7.5 (desvalorização extrema)
    # Impacto no agro: exportadores se beneficiam, mas insumos importados encarecem.
    # Aqui modelamos o efeito líquido como negativo para o risco de crédito
    # (piora da capacidade de pagamento de dívidas em USD, custo de máquinas).
    "cambio_usd_brl": {
        "referencia": 5.00,
        "estresse_max": 7.50,
        "peso": 0.20,
        "descricao": "Câmbio USD/BRL",
        "unidade": "R$/US$",
    },

    # Petróleo Brent (US$/barril): referência 75; estresse máximo = 130
    # Impacto direto no custo do diesel agrícola e dos fertilizantes nitrogenados.
    "petroleo_brent_usd": {
        "referencia": 75.0,
        "estresse_max": 130.0,
        "peso": 0.30,          # maior peso — impacto direto no custo de produção agro
        "descricao": "Petróleo Brent",
        "unidade": "US$/bbl",
    },

    # Índice de preço de fertilizantes (base 100 = média 2018-2022):
    # Referência = 120; estresse máximo = 250 (nível pós-2022 após conflito)
    "indice_fertilizantes": {
        "referencia": 120.0,
        "estresse_max": 250.0,
        "peso": 0.25,          # segundo maior peso — custo de produção agro
        "descricao": "Índice de Fertilizantes",
        "unidade": "pontos (base 100)",
    },

    # Taxa Selic (% a.a.): referência = 10.5; estresse máximo = 18.0
    # Custo do crédito rural — impacta diretamente a capacidade de rolar dívidas.
    "selic_pct": {
        "referencia": 10.5,
        "estresse_max": 18.0,
        "peso": 0.15,
        "descricao": "Taxa Selic",
        "unidade": "% a.a.",
    },

    # Índice de Risco Geopolítico (0–100, baseado no GPR Index):
    # Referência = 20 (período calmo); estresse máximo = 80 (conflitos regionais)
    "risco_geopolitico": {
        "referencia": 20.0,
        "estresse_max": 80.0,
        "peso": 0.10,
        "descricao": "Índice de Risco Geopolítico",
        "unidade": "0–100",
    },
}

# Fator de estresse mínimo e máximo (limites do intervalo de saída)
FATOR_ESTRESSE_MIN = 0.75
FATOR_ESTRESSE_MAX = 1.30

# Limiar de alerta para red flag de "exposição a choque macro"
LIMIAR_ALERTA_ESTRESSE = 1.10


# ---------------------------------------------------------------------------
# VALORES PADRÃO (CENÁRIO BASE)
# ---------------------------------------------------------------------------

VARIAVEIS_BASE = {
    "cambio_usd_brl": 5.65,
    "petroleo_brent_usd": 82.0,
    "indice_fertilizantes": 145.0,
    "selic_pct": 10.75,
    "risco_geopolitico": 28.0,
}


# ---------------------------------------------------------------------------
# COLETA DE VARIÁVEIS MACRO (MOCK)
# ---------------------------------------------------------------------------

def obter_variaveis_macro_atuais() -> dict:
    """
    MOCK — Substituir por chamadas reais às APIs listadas no cabeçalho do módulo.

    Em produção, esta função faria:
        cambio   = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json")
        petroleo = requests.get("https://www.alphavantage.co/query?function=BRENT&interval=daily&apikey=...")
        ...
    e retornaria um dicionário normalizado com os valores atuais.

    Por ora retorna o cenário base definido acima.
    """
    return VARIAVEIS_BASE.copy()


# ---------------------------------------------------------------------------
# CÁLCULO DO FATOR DE ESTRESSE MACRO
# ---------------------------------------------------------------------------

def calcular_fator_estresse_macro(variaveis: dict) -> dict:
    """
    Calcula o fator de estresse macroeconômico como multiplicador sobre o
    score idiossincrático do cliente.

    Lógica de ponderação:
        1. Para cada variável, calculamos seu "nível de estresse" normalizado
           no intervalo [0, 1]:
               stress_i = clamp((valor - referencia) / (estresse_max - referencia), 0, 1)
        2. Calculamos a média ponderada dos estresses individuais:
               estresse_ponderado = Σ (peso_i × stress_i) / Σ peso_i
        3. Mapeamos o estresse ponderado [0,1] para o fator final [MIN, MAX]:
               fator = MIN + estresse_ponderado × (MAX - MIN)

    Parâmetros:
        variaveis (dict): Dicionário com os valores das variáveis macro.
                          Chaves devem corresponder a PARAMETROS_MACRO.

    Retorna:
        dict com:
            fator_estresse (float): Multiplicador a ser aplicado no score
            estresse_ponderado (float): Valor bruto [0,1] antes do mapeamento
            detalhes_por_variavel (dict): Contribuição individual de cada variável
            interpretacao (str): Texto descritivo para o relatório
    """
    soma_peso = 0.0
    soma_ponderada = 0.0
    detalhes = {}

    for chave, params in PARAMETROS_MACRO.items():
        valor = variaveis.get(chave, params["referencia"])
        ref = params["referencia"]
        max_stress = params["estresse_max"]
        peso = params["peso"]

        # Normalização: quanto o valor diverge da referência em direção ao estresse máximo
        if max_stress == ref:
            stress_i = 0.0
        else:
            stress_i = (valor - ref) / (max_stress - ref)

        # Clamp [0, 1]: não damos crédito por ser melhor que a referência
        # (conservadorismo na análise de crédito)
        stress_i = max(0.0, min(1.0, stress_i))

        soma_ponderada += peso * stress_i
        soma_peso += peso

        detalhes[chave] = {
            "valor": valor,
            "stress_normalizado": round(stress_i, 4),
            "contribuicao_ponderada": round(peso * stress_i, 4),
            "descricao": params["descricao"],
            "unidade": params["unidade"],
        }

    estresse_ponderado = soma_ponderada / soma_peso if soma_peso > 0 else 0.0

    # Mapeamento linear: [0,1] → [FATOR_MIN, FATOR_MAX]
    fator_estresse = FATOR_ESTRESSE_MIN + estresse_ponderado * (
        FATOR_ESTRESSE_MAX - FATOR_ESTRESSE_MIN
    )
    fator_estresse = round(fator_estresse, 4)

    # Interpretação textual
    if fator_estresse < 0.90:
        interpretacao = "🟢 Ambiente macro favorável — bonifica o score do cliente."
    elif fator_estresse < 1.0:
        interpretacao = "🟡 Ambiente macro levemente favorável."
    elif fator_estresse < LIMIAR_ALERTA_ESTRESSE:
        interpretacao = "🟡 Ambiente macro neutro a levemente adverso."
    elif fator_estresse < 1.20:
        interpretacao = "🟠 Ambiente macro adverso — penaliza o score do cliente."
    else:
        interpretacao = "🔴 Ambiente macro em choque — penalização severa do score."

    return {
        "fator_estresse": fator_estresse,
        "estresse_ponderado": round(estresse_ponderado, 4),
        "detalhes_por_variavel": detalhes,
        "interpretacao": interpretacao,
        "acima_do_limiar": fator_estresse >= LIMIAR_ALERTA_ESTRESSE,
    }


# ---------------------------------------------------------------------------
# CENÁRIO DE TESTE: CHOQUE NO PETRÓLEO
# ---------------------------------------------------------------------------

def cenario_choque_petroleo(multiplicador_petroleo: float = 1.65) -> dict:
    """
    Simula uma alta abrupta no preço do petróleo e retorna o novo fator de
    estresse macro.

    Este é o cenário-chave para demonstração no pitch: mostra como um choque
    externo (ex: escalada de conflito no Oriente Médio, sanções) impacta
    diretamente o score de crédito de produtores rurais via custo de insumos.

    Parâmetros:
        multiplicador_petroleo (float): Fator de alta do petróleo sobre o
            valor base. Default = 1.65 → simula alta de 65% (ex: de $82 para $135).

    Retorna:
        dict com as variáveis macro do cenário de choque e o fator calculado.
    """
    vars_choque = VARIAVEIS_BASE.copy()

    # Petróleo sobe abrptamente
    vars_choque["petroleo_brent_usd"] = round(
        VARIAVEIS_BASE["petroleo_brent_usd"] * multiplicador_petroleo, 2
    )

    # Pressão secundária: petróleo caro → dólar valoriza → câmbio sobe
    vars_choque["cambio_usd_brl"] = round(
        VARIAVEIS_BASE["cambio_usd_brl"] * 1.15, 2
    )

    # Fertilizantes sobem junto (gás natural = insumo do nitrogênio)
    vars_choque["indice_fertilizantes"] = round(
        VARIAVEIS_BASE["indice_fertilizantes"] * 1.40, 2
    )

    # Risco geopolítico dispara (o que causou o choque)
    vars_choque["risco_geopolitico"] = min(100, VARIAVEIS_BASE["risco_geopolitico"] * 2.5)

    resultado = calcular_fator_estresse_macro(vars_choque)
    resultado["variaveis_cenario"] = vars_choque
    resultado["descricao_cenario"] = (
        f"⚠️ **Cenário: Choque no Petróleo (+{(multiplicador_petroleo-1)*100:.0f}%)**\n"
        f"Petróleo: US${vars_choque['petroleo_brent_usd']:.0f}/bbl | "
        f"Câmbio: R${vars_choque['cambio_usd_brl']:.2f}/US$ | "
        f"Fertilizantes: {vars_choque['indice_fertilizantes']:.0f} pts | "
        f"Risco Geop.: {vars_choque['risco_geopolitico']:.0f}"
    )

    return resultado


# ---------------------------------------------------------------------------
# BUSCA DE DADOS REAIS VIA GEMINI (Google AI)
# ---------------------------------------------------------------------------

import requests
import json
import re

import os

GEMINI_MODEL = "gemini-2.5-flash-lite"

def obter_gemini_api_key(api_key_fornecida: str = None) -> str:
    """Obtém a chave da API do Gemini via parâmetro, os.environ ou st.secrets."""
    if api_key_fornecida and api_key_fornecida.strip():
        return api_key_fornecida.strip()
    
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("GEMINI_API_KEY", "").strip()
        except Exception:
            pass
    return key


def buscar_variaveis_com_gemini(api_key: str = None) -> dict:
    """
    Usa a API do Google Gemini (com Grounding via Google Search) para buscar
    os valores atuais das variáveis macroeconômicas.

    Parâmetros:
        api_key (str): Chave da API do Google AI Studio (formato AIza...).

    Retorna:
        dict com as variáveis atualizadas e metadados da busca, ou dict com 'erro'.
    """
    key = obter_gemini_api_key(api_key)
    if not key:
        return {"erro": "Chave de API não configurada. Insira uma chave válida do Google AI Studio (aistudio.google.com/apikey) ou configure o Secret GEMINI_API_KEY."}

    prompt = (
        "Busque os valores ATUAIS e mais recentes das seguintes variáveis "
        "macroeconômicas. Retorne APENAS um JSON válido, sem markdown, sem "
        "explicação, sem texto antes ou depois. O JSON deve ter exatamente "
        "estas chaves:\n"
        "{\n"
        '  "cambio_usd_brl": <número decimal, cotação atual do dólar em reais>,\n'
        '  "petroleo_brent_usd": <número decimal, preço do barril de petróleo Brent em USD>,\n'
        '  "selic_pct": <número decimal, taxa Selic meta atual em % a.a.>,\n'
        '  "indice_fertilizantes": <número inteiro, índice de preço de fertilizantes base 100=média 2018-2022, estimar com base no preço atual da ureia>,\n'
        '  "risco_geopolitico": <número inteiro de 0 a 100, estimativa do nível de risco geopolítico global atual>,\n'
        '  "fonte": "<breve descrição das fontes consultadas>",\n'
        '  "data_consulta": "<data de hoje no formato YYYY-MM-DD>"\n'
        "}\n"
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={key}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Extrair texto da resposta
        texto = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "text" in part:
                    texto += part["text"]

        if not texto.strip():
            return {"erro": "O modelo Gemini retornou uma resposta vazia."}

        # Limpar possíveis backticks de markdown
        texto_limpo = texto.strip()
        texto_limpo = re.sub(r"^```(?:json)?\s*", "", texto_limpo)
        texto_limpo = re.sub(r"\s*```$", "", texto_limpo)

        resultado = json.loads(texto_limpo)

        # Validar que as chaves essenciais existem e são numéricas
        chaves_obrigatorias = [
            "cambio_usd_brl",
            "petroleo_brent_usd",
            "selic_pct",
            "indice_fertilizantes",
            "risco_geopolitico",
        ]
        for chave in chaves_obrigatorias:
            if chave not in resultado:
                return {"erro": f"Chave obrigatória ausente na resposta: {chave}"}
            resultado[chave] = float(resultado[chave])

        return resultado

    except Exception as e:
        msg = str(e)
        # Não vazar a chave na mensagem de erro
        if key and len(key) > 8:
            msg = msg.replace(key, "***")
        if "401" in msg or "Unauthorized" in msg:
            msg = "Chave de API inválida ou expirada. Gere uma nova chave gratuita em aistudio.google.com/apikey"
        elif "429" in msg or "Too Many Requests" in msg:
            msg = "Limite de requisições excedido (Rate Limit temporário do plano gratuito). Aguarde 15 a 30 segundos e tente novamente."
        elif "403" in msg or "Forbidden" in msg:
            msg = "Acesso negado. Verifique se a chave de API tem permissão para o modelo Gemini 1.5 Flash."
        elif "404" in msg:
            msg = f"Modelo {GEMINI_MODEL} não encontrado na API do Gemini."
        return {"erro": msg}
