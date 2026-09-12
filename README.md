# KrillTech Fin — Sistema de Risco de Crédito para o Agronegócio
### MVP para Demonstração em Hackathon

---

## 🚀 Como Rodar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

> **Python necessário:** 3.11+
> **Dependências:** streamlit, pandas, plotly (sem nenhuma API key externa)

### 2. Iniciar o sistema

```bash
streamlit run app.py
```

O sistema abrirá automaticamente em `http://localhost:8501`

---

## 📁 Estrutura do Projeto

```
KrillTech_Fin/
│
├── app.py                 # Interface Streamlit (ponto de entrada)
├── mock_data.py           # 7 clientes fictícios realistas (MOCK)
│
├── collector.py           # Módulo 1: Coletor & Parser de dados cadastrais
├── agro_risk.py           # Módulo 2: Risco agro-climático regional
├── macro_context.py       # Módulo 3: Contexto macroeconômico + fator de estresse
├── scoring_engine.py      # Módulo 4: Motor de scoring (0–1000) + red flags
├── report_generator.py    # Módulo 5: Gerador de relatório em Markdown
│
├── requirements.txt       # Dependências Python
└── README.md              # Este arquivo
```

---

## 🔑 Funcionalidades do MVP

| Feature | Status |
|---|---|
| Pipeline de 5 módulos desacoplados | ✅ |
| Score idiossincrático (0–1000) | ✅ |
| Fator de estresse macro (0.75×–1.30×) | ✅ |
| Score ajustado por macro | ✅ |
| Faixas de rating A/B/C/D | ✅ |
| Detecção de 5 tipos de red flags | ✅ |
| Recomendação operacional (limite + condições) | ✅ |
| Relatório completo em Markdown | ✅ |
| Dashboard com radar, gauge e waterfall | ✅ |
| **Simulador de cenário macro em tempo real** | ✅ |
| Preset: Choque de Petróleo (+65%) | ✅ |
| Tabela comparativa de impacto para todos os clientes | ✅ |
| Download do relatório (.md) | ✅ |

---

## 🎭 Roteiro de Demonstração no Pitch

### Ato 1 — Relatório de um cliente sólido (~2 min)
1. Selecionar **TriAgro Coop** (PR, Soja, 41 anos, Rating A)
2. Clicar em **Gerar Relatório**
3. Mostrar radar de dimensões + gauge + score idio vs. ajustado

### Ato 2 — Cliente com red flags (~2 min)
1. Selecionar **AmazonAgro** (PA, Dendê, pedido de RJ + embargo ambiental)
2. Gerar relatório → Rating D, 3 flags críticos, crédito negado
3. Mostrar como o sistema detecta e bloqueia automaticamente

### Ato 3 — Simulador de Choque (o mais importante, ~3 min)
1. Ir para a aba **Simulador de Cenário Macro**
2. Clicar em **🔴 Choque Petróleo (+65%)**
3. Mostrar: fator de estresse sobe de ~0.83× para ~1.21×
4. Apontar na tabela quais clientes trocam de faixa (B→C, C→D)
5. Fazer o slider de petróleo em tempo real para a banca visualizar
6. Frase de impacto: *"Em um choque de petróleo, nosso sistema reage em menos de 1 segundo e recomenda revisão do limite de 4 dos 7 clientes da carteira."*

---

## ⚠️ O que está Mockado e como Evoluiria para Produção

| Componente | Status MVP | Evolução para Produção |
|---|---|---|
| **Dados cadastrais** | Dicionário fixo em `mock_data.py` | API BrasilAPI/Receita Federal, Serpro DataValid |
| **Dados societários (QSA)** | Embutidos no mock | Receita Federal Webservice ou API Serpro |
| **Score fiscal** | Valor hardcoded por cliente | SINTEGRA, Nota Fiscal Eletrônica (NF-e) |
| **Score jurídico** | Valor hardcoded | DataJud (CNJ), Escavador, Jusbrasil |
| **Risco climático** | Tabela fixa por UF | INMET API, CPTEC/INPE, históricos CONAB |
| **Produtividade agrícola** | Tabela fixa por cultura | CONAB (PAM), EMBRAPA, MapBiomas |
| **Câmbio** | Valor fixo no baseline | BCB SGS série 1 (API gratuita) |
| **Petróleo Brent** | Valor fixo | Alpha Vantage, Yahoo Finance, Quandl |
| **Fertilizantes** | Valor fixo | World Bank Commodity Pink Sheet, CRU Group |
| **Selic** | Valor fixo | BCB SGS série 432 (API gratuita) |
| **Risco Geopolítico** | Valor fixo | GPR Index (Caldara & Iacoviello), CSV público |
| **Resumo em linguagem natural** | Templates parametrizados | Gemini Pro (Vertex AI) / GPT-4o |
| **Protestos** | Flag booleano mockado | Serasa Experian, SPC Brasil |
| **Pedido de RJ** | Flag booleano mockado | DataJud CNJ, SERASA |

### Próximos Passos para Produção

1. **Autenticação & multi-tenant**: cada instituição financeira acessa sua carteira isolada
2. **Banco de dados**: PostgreSQL para persistência de relatórios e histórico de score
3. **Scheduler**: re-score automático diário de toda a carteira com as variáveis macro atualizadas
4. **Alertas**: webhook/email quando cliente cruza uma faixa de rating ou novo red flag é detectado
5. **Calibração do modelo**: treinar os pesos de scoring com dados históricos de inadimplência real
6. **Auditoria**: log imutável de cada decisão para compliance regulatório (CMN/BCB)

---

*KrillTech Fin — MVP gerado para demonstração em hackathon. Dados simulados.*
