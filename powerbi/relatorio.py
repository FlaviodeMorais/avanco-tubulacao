# -*- coding: utf-8 -*-
"""Montagem do relatório (páginas e visuais) no formato Layout do Power BI."""

import json

LARGURA_PAGINA = 1280
ALTURA_PAGINA = 720

# Um campo é descrito por (papel, tabela, nome):
#   "m" = medida, "c" = coluna (agrupa), "s" = soma da coluna
M, C, S = "m", "c", "s"


def _apelidos(campos):
    """Gera um apelido de origem por tabela usada na consulta."""
    apelidos, ordem = {}, []
    for _, tabela, _nome in campos:
        if tabela not in apelidos:
            apelidos[tabela] = "t%d" % len(apelidos)
            ordem.append(tabela)
    return apelidos, ordem


def _consulta(campos):
    """Devolve (prototypeQuery, lista de queryRefs na mesma ordem dos campos)."""
    apelidos, ordem = _apelidos(campos)
    de = [{"Name": apelidos[t], "Entity": t, "Type": 0} for t in ordem]
    selecoes, refs = [], []
    for papel, tabela, nome in campos:
        origem = {"SourceRef": {"Source": apelidos[tabela]}}
        if papel == M:
            ref = "%s.%s" % (tabela, nome)
            selecoes.append({"Measure": {"Expression": origem, "Property": nome}, "Name": ref})
        elif papel == C:
            ref = "%s.%s" % (tabela, nome)
            selecoes.append({"Column": {"Expression": origem, "Property": nome}, "Name": ref})
        else:
            ref = "Sum(%s.%s)" % (tabela, nome)
            selecoes.append({
                "Aggregation": {
                    "Expression": {"Column": {"Expression": origem, "Property": nome}},
                    "Function": 0,
                },
                "Name": ref,
            })
        refs.append(ref)
    return {"Version": 2, "From": de, "Select": selecoes}, refs


def _titulo(texto):
    return {
        "title": [{
            "properties": {
                "text": {"expr": {"Literal": {"Value": "'%s'" % texto.replace("'", "")}}},
                "show": {"expr": {"Literal": {"Value": "true"}}},
            }
        }]
    }


def visual(nome, tipo, x, y, largura, altura, papeis, titulo=None, z=0):
    """papeis: dict papel_do_visual -> lista de campos (papel, tabela, coluna)."""
    campos = [campo for lista in papeis.values() for campo in lista]
    consulta, refs = _consulta(campos)

    projecoes, i = {}, 0
    for papel, lista in papeis.items():
        projecoes[papel] = [{"queryRef": refs[i + k]} for k in range(len(lista))]
        i += len(lista)

    config = {
        "name": nome,
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": z, "width": largura, "height": altura,
                         "tabOrder": z},
        }],
        "singleVisual": {
            "visualType": tipo,
            "projections": projecoes,
            "prototypeQuery": consulta,
            "drillFilterOtherVisuals": True,
            "objects": {},
            "vcObjects": _titulo(titulo) if titulo else {},
        },
    }
    return {
        "x": x, "y": y, "z": z, "width": largura, "height": altura,
        "config": json.dumps(config, ensure_ascii=False),
        "filters": "[]",
    }


def pagina(indice, nome, titulo, visuais):
    return {
        "id": indice,
        "name": nome,
        "displayName": titulo,
        "filters": "[]",
        "ordinal": indice,
        "visualContainers": visuais,
        "config": "{}",
        "displayOption": 1,
        "width": LARGURA_PAGINA,
        "height": ALTURA_PAGINA,
    }


def _cartoes(prefixo, medidas, y, altura=92, margem=16, folga=16):
    """Distribui cartões (medida única) numa faixa horizontal."""
    n = len(medidas)
    largura = (LARGURA_PAGINA - 2 * margem - folga * (n - 1)) // n
    saida = []
    for i, rotulo in enumerate(medidas):
        saida.append(visual(
            "%s_card%d" % (prefixo, i), "card",
            margem + i * (largura + folga), y, largura, altura,
            {"Values": [(M, "Medidas", rotulo)]}, titulo=rotulo, z=i))
    return saida


def construir_secoes():
    secoes = []

    # ---------------------------------------------------------------- Página 1
    v = _cartoes("p1", ["Peso Total (ton)", "Fabricado (ton)", "Liberado END (ton)",
                        "% Concluido (Liberado END)", "Qtd Spools"], y=12)
    v += [
        visual("p1_slicer", "slicer", 16, 116, 232, 288,
               {"Values": [(C, "Unidades", "Unidade")]}, titulo="Unidade"),
        visual("p1_curva", "lineChart", 264, 116, 1000, 288, {
            "Category": [(C, "Meses", "Mes")],
            "Series": [(C, "Etapas", "Etapa")],
            "Y": [(M, "Medidas", "Avanco Acumulado (ton)")],
        }, titulo="Curva de avanco acumulado por etapa (ton)"),
        visual("p1_sop", "clusteredBarChart", 16, 420, 616, 284, {
            "Category": [(C, "Ranking_SOP", "SOP")],
            "Y": [(S, "Ranking_SOP", "Peso Total (ton)"),
                  (S, "Ranking_SOP", "Peso Liberado (ton)")],
        }, titulo="Pacotes SOP - previsto x liberado (ton)"),
        visual("p1_mes", "clusteredColumnChart", 648, 420, 616, 284, {
            "Category": [(C, "Meses", "Mes")],
            "Y": [(M, "Medidas", "Avanco no Mes (ton)")],
        }, titulo="Avanco realizado no mes (ton)"),
    ]
    secoes.append(pagina(0, "pagina1", "Visao Geral", v))

    # ---------------------------------------------------------------- Página 2
    v = [
        visual("p2_slicer", "slicer", 16, 16, 240, 400,
               {"Values": [(C, "Meses", "Mes")]}, titulo="Mes de referencia"),
        visual("p2_matriz", "pivotTable", 272, 16, 992, 400, {
            "Rows": [(C, "Unidades", "Unidade")],
            "Columns": [(C, "Etapas", "Etapa")],
            "Values": [(M, "Medidas", "Avanco Acumulado (ton)")],
        }, titulo="Avanco acumulado por unidade e etapa (ton)"),
        visual("p2_curva", "lineChart", 16, 432, 1248, 272, {
            "Category": [(C, "Meses", "Mes")],
            "Series": [(C, "Unidades", "Unidade")],
            "Y": [(M, "Medidas", "Liberado END Acumulado (ton)")],
        }, titulo="Liberado END acumulado por unidade (ton)"),
    ]
    secoes.append(pagina(1, "pagina2", "Por Unidade", v))

    # ---------------------------------------------------------------- Página 3
    v = [
        visual("p3_tabela", "tableEx", 16, 16, 760, 688, {
            "Values": [(C, "Ranking_SOP", "SOP"),
                       (S, "Ranking_SOP", "Spools"),
                       (S, "Ranking_SOP", "Peso Total (ton)"),
                       (S, "Ranking_SOP", "Peso Fabricado (ton)"),
                       (S, "Ranking_SOP", "Peso Liberado (ton)"),
                       (S, "Ranking_SOP", "% Liberado")],
        }, titulo="Avanco por pacote SOP"),
        visual("p3_curva", "lineChart", 792, 16, 472, 340, {
            "Category": [(C, "Meses", "Mes")],
            "Series": [(C, "Etapas", "Etapa")],
            "Y": [(M, "Medidas", "Avanco SOP (ton)")],
        }, titulo="Curva do SOP selecionado (ton)"),
        visual("p3_slicer", "slicer", 792, 372, 472, 332,
               {"Values": [(C, "Ranking_SOP", "SOP")]}, titulo="Pacote SOP"),
    ]
    secoes.append(pagina(2, "pagina3", "Pacotes SOP", v))

    # ---------------------------------------------------------------- Página 4
    v = [
        visual("p4_slicer_un", "slicer", 16, 16, 240, 220,
               {"Values": [(C, "Unidades", "Unidade")]}, titulo="Unidade"),
        visual("p4_slicer_st", "slicer", 16, 248, 240, 456,
               {"Values": [(C, "Spools", "Status Montagem")]}, titulo="Status de montagem"),
        visual("p4_tabela", "tableEx", 272, 16, 992, 688, {
            "Values": [(C, "Spools", "ISO"), (C, "Spools", "Spool"), (C, "Spools", "Linha"),
                       (C, "Spools", "Unidade"), (S, "Spools", "Peso_kg"),
                       (C, "Spools", "Status Fabricacao"), (C, "Spools", "Status Montagem")],
        }, titulo="Spools"),
    ]
    secoes.append(pagina(3, "pagina4", "Spools", v))

    # ---------------------------------------------------------------- Página 5
    v = _cartoes("p5", ["Juntas Total", "Juntas Soldadas", "% Juntas Soldadas", "% Reparo"], y=12)
    v += [
        visual("p5_curva", "lineChart", 16, 116, 624, 288, {
            "Category": [(C, "Meses", "Mes")],
            "Series": [(C, "Juntas_Curva", "Serie")],
            "Y": [(M, "Medidas", "Juntas Acumuladas")],
        }, titulo="Juntas acumuladas por mes"),
        visual("p5_diam", "clusteredColumnChart", 656, 116, 608, 288, {
            "Category": [(C, "Reparos_Diametro", "Diametro")],
            "Y": [(S, "Reparos_Diametro", "% Reparo")],
        }, titulo="Indice de reparo por diametro (%)"),
        visual("p5_tabela", "tableEx", 16, 420, 1248, 284, {
            "Values": [(C, "Soldadores", "Soldador"), (S, "Soldadores", "Juntas"),
                       (S, "Soldadores", "Soldadas"), (S, "Soldadores", "Reparos"),
                       (S, "Soldadores", "% Reparo"), (S, "Soldadores", "% Conclusao")],
        }, titulo="Ranking de soldadores"),
    ]
    secoes.append(pagina(4, "pagina5", "Juntas e Soldadores", v))

    # ---------------------------------------------------------------- Página 6
    v = [
        visual("p6_material", "lineChart", 16, 16, 624, 320, {
            "Category": [(C, "Meses", "Mes")],
            "Series": [(C, "Materiais", "Material")],
            "Y": [(M, "Medidas", "Fabricado por Material (ton)")],
        }, titulo="Fabricado acumulado por material (ton)"),
        visual("p6_tempo", "clusteredColumnChart", 656, 16, 608, 320, {
            "Category": [(C, "Materiais", "Material")],
            "Series": [(C, "Tempo_Medio", "Tipo")],
            "Y": [(M, "Medidas", "Dias Medios")],
        }, titulo="Tempo medio por material (dias)"),
    ]
    v += _cartoes("p6", ["% Pintura", "% Isolamento", "% Peso com STH", "% Medio Avanco SOP"],
                  y=352, altura=100)
    v += [
        visual("p6_linhas", "tableEx", 16, 468, 1248, 236, {
            "Values": [(C, "Ranking_Linhas", "Linha"), (S, "Ranking_Linhas", "Spools"),
                       (S, "Ranking_Linhas", "Peso Total (ton)"),
                       (S, "Ranking_Linhas", "Peso Liberado (ton)"),
                       (S, "Ranking_Linhas", "% Liberado")],
        }, titulo="Linhas com maior peso"),
    ]
    secoes.append(pagina(5, "pagina6", "Materiais e Acabamento", v))

    return secoes


def construir_layout():
    return {
        "id": 0,
        "resourcePackages": [],
        "sections": construir_secoes(),
        "config": json.dumps({
            "version": "5.43",
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True,
            "settings": {"useStylableVisualContainerHeader": True},
        }),
        "layoutOptimization": 0,
        "publicCustomVisuals": [],
        "pods": [],
    }
