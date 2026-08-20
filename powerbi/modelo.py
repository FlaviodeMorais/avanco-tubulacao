# -*- coding: utf-8 -*-
"""Definição do modelo semântico (tabelas, colunas, medidas e relacionamentos)."""

TXT, INT, NUM, DATA = "string", "int64", "double", "dateTime"

FMT_TON = "#,0.000"
FMT_INT = "#,0"
FMT_PCT = "0.0%"
FMT_NUM1 = "#,0.0"

# nome -> (colunas, ocultar_tabela)
# coluna: (nome, tipo, formato|None, oculta)
TABELAS = {
    "Meses": [
        ("Mes", TXT, None, False),
        ("Ordem", INT, FMT_INT, True),
        ("FimDoMes", DATA, None, False),
        ("Ano", INT, "0", False),
        ("MesNum", INT, FMT_INT, True),
    ],
    "Etapas": [
        ("Etapa", TXT, None, False),
        ("OrdemEtapa", INT, FMT_INT, True),
    ],
    "Unidades": [("Unidade", TXT, None, False)],
    "Materiais": [("Material", TXT, None, False)],
    "Avanco_Unidade": [
        ("Unidade", TXT, None, False),
        ("Etapa", TXT, None, False),
        ("Ordem", INT, FMT_INT, True),
        ("Ton_Acumulado", NUM, FMT_TON, False),
    ],
    "Avanco_SOP": [
        ("SOP", TXT, None, False),
        ("Etapa", TXT, None, False),
        ("Ordem", INT, FMT_INT, True),
        ("Ton_Acumulado", NUM, FMT_TON, False),
    ],
    "Spools": [
        ("ISO", TXT, None, False),
        ("Spool", TXT, None, False),
        ("Linha", TXT, None, False),
        ("Unidade", TXT, None, False),
        ("Peso_kg", NUM, FMT_NUM1, False),
        ("CodStatusFab", TXT, None, True),
        ("CodStatusMon", TXT, None, True),
        ("Status Fabricacao", TXT, None, False),
        ("Status Montagem", TXT, None, False),
        ("Peso_ton", NUM, FMT_TON, False),
    ],
    "Ranking_SOP": [
        ("SOP", TXT, None, False),
        ("Linhas", INT, FMT_INT, False),
        ("STHs", INT, FMT_INT, False),
        ("Spools", INT, FMT_INT, False),
        ("Peso Total (ton)", NUM, FMT_TON, False),
        ("Peso Fabricado (ton)", NUM, FMT_TON, False),
        ("Peso Liberado (ton)", NUM, FMT_TON, False),
        ("% Fabricado", NUM, FMT_NUM1, False),
        ("% Liberado", NUM, FMT_NUM1, False),
    ],
    "Ranking_Linhas": [
        ("Linha", TXT, None, False),
        ("Spools", INT, FMT_INT, False),
        ("Peso Total (ton)", NUM, FMT_TON, False),
        ("Peso Liberado (ton)", NUM, FMT_TON, False),
        ("% Liberado", NUM, FMT_NUM1, False),
    ],
    "Material_Fabricado": [
        ("Material", TXT, None, False),
        ("Ordem", INT, FMT_INT, True),
        ("Ton_Fabricado_Acumulado", NUM, FMT_TON, False),
    ],
    "Tempo_Medio": [
        ("Material", TXT, None, False),
        ("Tipo", TXT, None, False),
        ("Dias", NUM, FMT_NUM1, False),
        ("Amostra", INT, FMT_INT, False),
    ],
    "KPIs": [
        ("Peso Total (ton)", NUM, FMT_TON, False),
        ("Spools (qtd)", NUM, FMT_INT, False),
        ("Spools Nao Iniciados", NUM, FMT_INT, False),
        ("Nao Iniciados (ton)", NUM, FMT_TON, False),
        ("Pacotes SOP", NUM, FMT_INT, False),
        ("% Medio Avanco SOP", NUM, FMT_NUM1, False),
        ("SOPs Concluidos", NUM, FMT_INT, False),
        ("SOP Liberado (ton)", NUM, FMT_TON, False),
        ("Sistemas STH", NUM, FMT_INT, False),
        ("STH Iniciados", NUM, FMT_INT, False),
        ("STH Concluidos", NUM, FMT_INT, False),
        ("% Peso com STH", NUM, FMT_NUM1, False),
        ("Pintura Prevista (m2)", NUM, FMT_NUM1, False),
        ("Pintura Realizada (m2)", NUM, FMT_NUM1, False),
        ("% Pintura", NUM, FMT_NUM1, False),
        ("Isolamento Previsto (m2)", NUM, FMT_NUM1, False),
        ("Isolamento Realizado (m2)", NUM, FMT_NUM1, False),
        ("% Isolamento", NUM, FMT_NUM1, False),
        ("AC ate 2pol Previsto (ton)", NUM, FMT_TON, False),
        ("AC ate 2pol Realizado (ton)", NUM, FMT_TON, False),
        ("% AC ate 2pol", NUM, FMT_NUM1, False),
    ],
    "Juntas_KPIs": [
        ("Juntas (total)", NUM, FMT_INT, False),
        ("Soldadas", NUM, FMT_INT, False),
        ("Liberadas END", NUM, FMT_INT, False),
        ("Com Visual de Solda", NUM, FMT_INT, False),
        ("Com Ensaio END", NUM, FMT_INT, False),
        ("Reparos 1a", NUM, FMT_INT, False),
        ("Reparos 2a", NUM, FMT_INT, False),
        ("% Soldadas", NUM, FMT_NUM1, False),
        ("% Liberadas END", NUM, FMT_NUM1, False),
        ("% Reparo", NUM, FMT_NUM1, False),
        ("END RX Previsto", NUM, FMT_INT, False),
        ("END US Previsto", NUM, FMT_INT, False),
        ("END RX Realizado", NUM, FMT_INT, False),
        ("END US Realizado", NUM, FMT_INT, False),
    ],
    "Soldadores": [
        ("Soldador", TXT, None, False),
        ("Juntas", INT, FMT_INT, False),
        ("Soldadas", INT, FMT_INT, False),
        ("Reparos", INT, FMT_INT, False),
        ("Reparos 2a", INT, FMT_INT, False),
        ("Liberadas END", INT, FMT_INT, False),
        ("% Reparo", NUM, FMT_NUM1, False),
        ("% Conclusao", NUM, FMT_NUM1, False),
    ],
    "Reparos_Diametro": [
        ("Diametro", TXT, None, False),
        ("Juntas", INT, FMT_INT, False),
        ("Reparos", INT, FMT_INT, False),
        ("% Reparo", NUM, FMT_NUM1, False),
    ],
    "Juntas_Curva": [
        ("Mes", TXT, None, False),
        ("Serie", TXT, None, False),
        ("Juntas", INT, FMT_INT, False),
    ],
    "Juntas_Material": [
        ("Mes", TXT, None, False),
        ("Material", TXT, None, False),
        ("Juntas Soldadas", INT, FMT_INT, False),
    ],
    "Medidas": [("Coluna", INT, None, True)],
}

# Ordenação: coluna de texto ordenada por uma coluna numérica.
ORDENAR_POR = {
    ("Meses", "Mes"): "Ordem",
    ("Etapas", "Etapa"): "OrdemEtapa",
}

# (nome, expressão DAX, formato, pasta)
MEDIDAS = [
    # --- Escopo (vem da tabela de spools, responde ao filtro de Unidade) ---
    ("Peso Total (ton)", "DIVIDE(SUM(Spools[Peso_kg]), 1000)", FMT_TON, "1 Escopo"),
    ("Qtd Spools", "COUNTROWS(Spools)", FMT_INT, "1 Escopo"),
    ("Qtd Nao Iniciados",
     'CALCULATE(COUNTROWS(Spools), Spools[CodStatusMon] = "36")', FMT_INT, "1 Escopo"),
    ("Peso Nao Iniciado (ton)",
     'DIVIDE(CALCULATE(SUM(Spools[Peso_kg]), Spools[CodStatusMon] = "36"), 1000)',
     FMT_TON, "1 Escopo"),
    ("% Nao Iniciado",
     "DIVIDE([Peso Nao Iniciado (ton)], [Peso Total (ton)])", FMT_PCT, "1 Escopo"),

    # --- Curva de avanço ---
    ("Avanco Acumulado (ton)", "SUM(Avanco_Unidade[Ton_Acumulado])", FMT_TON, "2 Avanco"),
    ("Avanco no Mes (ton)",
     "VAR OrdemAtual = MAX(Meses[Ordem])\n"
     "VAR Atual = [Avanco Acumulado (ton)]\n"
     "VAR Anterior =\n"
     "    CALCULATE(\n"
     "        SUM(Avanco_Unidade[Ton_Acumulado]),\n"
     "        ALL(Meses),\n"
     "        Meses[Ordem] = OrdemAtual - 1\n"
     "    )\n"
     "RETURN\n"
     "    Atual - Anterior",
     FMT_TON, "2 Avanco"),
    ("Saldo a Realizar (ton)",
     "[Peso Total (ton)] - [Avanco Acumulado (ton)]", FMT_TON, "2 Avanco"),
    ("% Avanco", "DIVIDE([Avanco Acumulado (ton)], [Peso Total (ton)])", FMT_PCT, "2 Avanco"),
    ("Ultimo Mes", "MAXX(ALLSELECTED(Meses), Meses[Ordem])", FMT_INT, "2 Avanco"),
    ("Fabricado Acumulado (ton)",
     'CALCULATE(SUM(Avanco_Unidade[Ton_Acumulado]), ALL(Etapas), Etapas[Etapa] = "Fabricado")',
     FMT_TON, "2 Avanco"),
    ("Liberado END Acumulado (ton)",
     'CALCULATE(SUM(Avanco_Unidade[Ton_Acumulado]), ALL(Etapas), Etapas[Etapa] = "Liberado END")',
     FMT_TON, "2 Avanco"),

    # --- Posição atual por etapa (não somam meses; usam o último mês visível) ---
    ("Fabricado (ton)",
     'CALCULATE(\n'
     '    SUM(Avanco_Unidade[Ton_Acumulado]),\n'
     '    Meses[Ordem] = [Ultimo Mes],\n'
     '    ALL(Etapas),\n'
     '    Etapas[Etapa] = "Fabricado"\n'
     ')', FMT_TON, "3 Posicao atual"),
    ("Soldado (ton)",
     'CALCULATE(\n'
     '    SUM(Avanco_Unidade[Ton_Acumulado]),\n'
     '    Meses[Ordem] = [Ultimo Mes],\n'
     '    ALL(Etapas),\n'
     '    Etapas[Etapa] = "Soldado"\n'
     ')', FMT_TON, "3 Posicao atual"),
    ("Liberado END (ton)",
     'CALCULATE(\n'
     '    SUM(Avanco_Unidade[Ton_Acumulado]),\n'
     '    Meses[Ordem] = [Ultimo Mes],\n'
     '    ALL(Etapas),\n'
     '    Etapas[Etapa] = "Liberado END"\n'
     ')', FMT_TON, "3 Posicao atual"),
    ("Teste Hidrostatico (ton)",
     'CALCULATE(\n'
     '    SUM(Avanco_Unidade[Ton_Acumulado]),\n'
     '    Meses[Ordem] = [Ultimo Mes],\n'
     '    ALL(Etapas),\n'
     '    Etapas[Etapa] = "Teste Hidrostático"\n'
     ')', FMT_TON, "3 Posicao atual"),
    ("% Fabricado", "DIVIDE([Fabricado (ton)], [Peso Total (ton)])", FMT_PCT, "3 Posicao atual"),
    ("% Concluido (Liberado END)",
     "DIVIDE([Liberado END (ton)], [Peso Total (ton)])", FMT_PCT, "3 Posicao atual"),

    # --- SOP / linhas ---
    ("Avanco SOP (ton)", "SUM(Avanco_SOP[Ton_Acumulado])", FMT_TON, "4 SOP"),
    ("Peso Liberado SOP (ton)", "SUM(Ranking_SOP[Peso Liberado (ton)])", FMT_TON, "4 SOP"),
    ("% Medio Avanco SOP", "DIVIDE(AVERAGE(Ranking_SOP[% Liberado]), 100)", FMT_PCT, "4 SOP"),

    # --- Fabricação por material ---
    ("Fabricado por Material (ton)",
     "SUM(Material_Fabricado[Ton_Fabricado_Acumulado])", FMT_TON, "5 Material"),
    ("Dias Medios", "AVERAGE(Tempo_Medio[Dias])", FMT_NUM1, "5 Material"),

    # --- Juntas / soldagem ---
    ("Juntas Total", "SUM(Juntas_KPIs[Juntas (total)])", FMT_INT, "6 Juntas"),
    ("Juntas Soldadas", "SUM(Juntas_KPIs[Soldadas])", FMT_INT, "6 Juntas"),
    ("Juntas Liberadas END", "SUM(Juntas_KPIs[Liberadas END])", FMT_INT, "6 Juntas"),
    ("% Juntas Soldadas", "DIVIDE([Juntas Soldadas], [Juntas Total])", FMT_PCT, "6 Juntas"),
    ("% Juntas Liberadas END",
     "DIVIDE([Juntas Liberadas END], [Juntas Total])", FMT_PCT, "6 Juntas"),
    ("Reparos", "SUM(Juntas_KPIs[Reparos 1a])", FMT_INT, "6 Juntas"),
    ("% Reparo", "DIVIDE([Reparos], [Juntas Soldadas])", FMT_PCT, "6 Juntas"),
    ("Juntas Acumuladas", "SUM(Juntas_Curva[Juntas])", FMT_INT, "6 Juntas"),
    ("Juntas Soldadas por Material", "SUM(Juntas_Material[Juntas Soldadas])", FMT_INT, "6 Juntas"),

    # --- Pintura / isolamento / STH ---
    ("% Pintura",
     "DIVIDE(SUM(KPIs[Pintura Realizada (m2)]), SUM(KPIs[Pintura Prevista (m2)]))",
     FMT_PCT, "7 Acabamento"),
    ("% Isolamento",
     "DIVIDE(SUM(KPIs[Isolamento Realizado (m2)]), SUM(KPIs[Isolamento Previsto (m2)]))",
     FMT_PCT, "7 Acabamento"),
    ("% Peso com STH", "DIVIDE(SUM(KPIs[% Peso com STH]), 100)", FMT_PCT, "7 Acabamento"),
]

# (tabela_muitos, coluna_muitos, tabela_um, coluna_um)
RELACIONAMENTOS = [
    ("Avanco_Unidade", "Ordem", "Meses", "Ordem"),
    ("Avanco_SOP", "Ordem", "Meses", "Ordem"),
    ("Material_Fabricado", "Ordem", "Meses", "Ordem"),
    ("Juntas_Curva", "Mes", "Meses", "Mes"),
    ("Juntas_Material", "Mes", "Meses", "Mes"),
    ("Avanco_Unidade", "Etapa", "Etapas", "Etapa"),
    ("Avanco_SOP", "Etapa", "Etapas", "Etapa"),
    ("Avanco_Unidade", "Unidade", "Unidades", "Unidade"),
    ("Spools", "Unidade", "Unidades", "Unidade"),
    ("Material_Fabricado", "Material", "Materiais", "Material"),
    ("Tempo_Medio", "Material", "Materiais", "Material"),
    ("Juntas_Material", "Material", "Materiais", "Material"),
    ("Avanco_SOP", "SOP", "Ranking_SOP", "SOP"),
]
