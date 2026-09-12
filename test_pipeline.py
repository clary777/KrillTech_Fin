# -*- coding: utf-8 -*-
"""Script de teste end-to-end da pipeline KrillTech Fin."""

from mock_data import CLIENTES
from collector import coletar_dados_cliente
from agro_risk import calcular_score_agro
from macro_context import calcular_fator_estresse_macro, VARIAVEIS_BASE, cenario_choque_petroleo
from scoring_engine import calcular_score_final
from report_generator import gerar_relatorio

PASS = "OK"
FAIL = "FALHOU"
erros = []

def check(nome, condicao):
    status = PASS if condicao else FAIL
    print(f"  [{status}] {nome}")
    if not condicao:
        erros.append(nome)

# ─── TESTE 1: Fazenda São Benedito (perfil A) ───────────────────────────────
print("\n=== TESTE 1: Fazenda Sao Benedito (perfil A esperado) ===")
cnpj   = "12.345.678/0001-90"
dados  = coletar_dados_cliente(cnpj)
agro   = calcular_score_agro(dados["uf"], dados["cultura_principal"])
macro  = calcular_fator_estresse_macro(VARIAVEIS_BASE)
sc     = calcular_score_final(dados, agro, macro)
relat  = gerar_relatorio(dados, agro, macro, sc)

print(f"  Score Idiossincrático : {sc['score_idiossincrático']}")
print(f"  Score Ajustado        : {sc['score_ajustado']}")
print(f"  Rating                : {sc['rating']}")
print(f"  Fator Estresse Macro  : {macro['fator_estresse']}")
print(f"  Red Flags             : {sc['n_red_flags']}")
print(f"  Limite Credito        : R$ {sc['limite_credito_brl']:,.0f}")

check("dados retornados", bool(dados))
check("score idiossincrático > 0", sc["score_idiossincrático"] > 0)
check("rating em A/B/C/D", sc["rating"] in ["A", "B", "C", "D"])
check("rating esperado A ou B", sc["rating"] in ["A", "B"])
check("relatorio gerado (len > 100)", len(relat) > 100)
check("fator de estresse entre 0.75 e 1.30", 0.75 <= macro["fator_estresse"] <= 1.30)

# ─── TESTE 2: AmazonAgro (perfil D — RJ + embargo + inadimplência) ──────────
print("\n=== TESTE 2: AmazonAgro (perfil D esperado) ===")
cnpj2  = "19.876.543/0001-77"
dados2 = coletar_dados_cliente(cnpj2)
agro2  = calcular_score_agro(dados2["uf"], dados2["cultura_principal"])
sc2    = calcular_score_final(dados2, agro2, macro)

print(f"  Score Ajustado        : {sc2['score_ajustado']}")
print(f"  Rating                : {sc2['rating']}")
print(f"  Red Flags             : {sc2['n_red_flags']}")
criticos = [f for f in sc2["red_flags"] if f["severidade"] == "CRITICO"]
altos    = [f for f in sc2["red_flags"] if f["severidade"] == "ALTO"]
print(f"  Criticos: {[f['codigo'] for f in criticos]}")
print(f"  Altos:    {[f['codigo'] for f in altos]}")

check("tem flag critica", sc2["tem_flag_critica"])
check("rating D", sc2["rating"] == "D")
check("limite credito = 0", sc2["limite_credito_brl"] == 0)
check("n_red_flags >= 3", sc2["n_red_flags"] >= 3)

# ─── TESTE 3: Choque de Petróleo ─────────────────────────────────────────────
print("\n=== TESTE 3: Cenario Choque de Petroleo (+65%) ===")
choque       = cenario_choque_petroleo(1.65)
macro_choque = calcular_fator_estresse_macro(choque["variaveis_cenario"])
sc_choque    = calcular_score_final(dados, agro, macro_choque)  # cliente Fazenda São Benedito

print(f"  Petroleo simulado     : US${choque['variaveis_cenario']['petroleo_brent_usd']}")
print(f"  Fator Estresse BASE   : {macro['fator_estresse']}")
print(f"  Fator Estresse CHOQUE : {macro_choque['fator_estresse']}")
print(f"  Score BASE            : {sc['score_ajustado']}")
print(f"  Score CHOQUE          : {sc_choque['score_ajustado']}")
print(f"  Variacao de score     : {sc_choque['score_ajustado'] - sc['score_ajustado']:+.1f}")

check("fator choque > fator base", macro_choque["fator_estresse"] > macro["fator_estresse"])
check("score choque < score base (penaliza)", sc_choque["score_ajustado"] < sc["score_ajustado"])
check("fator choque acima do limiar (>= 1.10)", macro_choque["acima_do_limiar"])

# ─── TESTE 4: Todos os 7 clientes ─────────────────────────────────────────────
print("\n=== TESTE 4: Pipeline para todos os 7 clientes ===")
for cnpj_iter, cliente in CLIENTES.items():
    d = coletar_dados_cliente(cnpj_iter)
    a = calcular_score_agro(d["uf"], d["cultura_principal"])
    s = calcular_score_final(d, a, macro)
    ok = s["rating"] in ["A", "B", "C", "D"] and 0 <= s["score_ajustado"] <= 1000
    print(f"  {cliente['nome_fantasia']:<30} Score: {s['score_ajustado']:>6.1f}  Rating: {s['rating']}  Flags: {s['n_red_flags']}  {'OK' if ok else 'FALHOU'}")
    if not ok:
        erros.append(f"cliente {cnpj_iter}")

# ─── RESULTADO FINAL ─────────────────────────────────────────────────────────
print("\n" + "="*60)
if not erros:
    print("RESULTADO: TODOS OS TESTES PASSARAM - MVP pronto para rodar!")
else:
    print(f"RESULTADO: {len(erros)} FALHA(S): {erros}")
print("="*60)
