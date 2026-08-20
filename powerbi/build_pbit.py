# -*- coding: utf-8 -*-
"""Gera o modelo do Power BI a partir das definições em consultas.py / modelo.py / relatorio.py.

Saídas (todas em `powerbi/`):
  ControlTub-Avanco-Tubulacao.pbit          modelo do Power BI (abrir e "Salvar como" .pbix)
  ControlTub-Avanco-Tubulacao.pbip          projeto do Power BI (plano B, formato de pastas)
  ControlTub-Avanco-Tubulacao.SemanticModel/
  ControlTub-Avanco-Tubulacao.Report/
  modelo/consultas.pq                       consultas M em texto (para colar à mão)
  modelo/medidas.dax                        medidas DAX em texto (para colar à mão)

Uso:  python3 powerbi/build_pbit.py
"""

import io
import json
import os
import shutil
import sys
import uuid
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import consultas  # noqa: E402
import modelo  # noqa: E402
import relatorio  # noqa: E402

NOME = "ControlTub-Avanco-Tubulacao"
NOME_MODELO = "ControlTub - Avanço de Tubulação"

NAMESPACE = uuid.UUID("6f1d0a4c-2f5e-4d38-9a1b-controltub00".replace("controltub00", "b7c3d1e9f204"))


def _linhas(texto):
    """O TMSL guarda expressões como lista de linhas."""
    return texto.replace("\r\n", "\n").split("\n")


def _coluna(tabela, nome, tipo, formato, oculta):
    col = {
        "name": nome,
        "dataType": tipo,
        "sourceColumn": nome,
        "summarizeBy": "sum" if tipo in (modelo.NUM, modelo.INT) else "none",
        "annotations": [{"name": "SummarizationSetBy", "value": "Automatic"}],
    }
    if tipo == modelo.DATA:
        col["formatString"] = "General Date"
    elif formato:
        col["formatString"] = formato
    if oculta:
        col["isHidden"] = True
        col["summarizeBy"] = "none"
    ordenar = modelo.ORDENAR_POR.get((tabela, nome))
    if ordenar:
        col["sortByColumn"] = ordenar
    return col


def _tabela(nome):
    colunas = [_coluna(nome, *c) for c in modelo.TABELAS[nome]]
    tabela = {
        "name": nome,
        "columns": colunas,
        "partitions": [{
            "name": nome,
            "mode": "import",
            "source": {"type": "m", "expression": _linhas(consultas.CONSULTAS[nome])},
        }],
        "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
    }
    if nome == "Medidas":
        tabela["measures"] = [
            {
                "name": med_nome,
                "expression": _linhas(expressao),
                "formatString": formato,
                "displayFolder": pasta,
            }
            for med_nome, expressao, formato, pasta in modelo.MEDIDAS
        ]
    return tabela


def construir_bim():
    tabelas = [_tabela(nome) for nome in modelo.TABELAS]

    relacionamentos = []
    for de_tabela, de_coluna, para_tabela, para_coluna in modelo.RELACIONAMENTOS:
        chave = "%s-%s-%s-%s" % (de_tabela, de_coluna, para_tabela, para_coluna)
        relacionamentos.append({
            "name": str(uuid.uuid5(NAMESPACE, chave)),
            "fromTable": de_tabela,
            "fromColumn": de_coluna,
            "toTable": para_tabela,
            "toColumn": para_coluna,
        })

    expressoes = [
        {
            "name": "FonteDados",
            "kind": "m",
            "expression": _linhas(consultas.PARAMETRO_FONTE),
            "annotations": [
                {"name": "PBI_NavigationStepName", "value": "Navegação"},
                {"name": "PBI_ResultType", "value": "Text"},
            ],
        },
        {
            "name": "fnCarregar",
            "kind": "m",
            "expression": _linhas(consultas.FN_CARREGAR),
            "annotations": [
                {"name": "PBI_NavigationStepName", "value": "Navegação"},
                {"name": "PBI_ResultType", "value": "Function"},
            ],
        },
    ]

    ordem = ["FonteDados", "fnCarregar"] + list(modelo.TABELAS)

    return {
        "name": NOME_MODELO,
        "compatibilityLevel": 1550,
        "model": {
            "culture": "pt-BR",
            "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "pt-BR",
            "tables": tabelas,
            "relationships": relacionamentos,
            "expressions": expressoes,
            "annotations": [
                {"name": "PBI_QueryOrder", "value": json.dumps(ordem, ensure_ascii=False)},
                {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
                {"name": "PBIDesktopVersion", "value": "2.140.1454.0 (25.08)"},
            ],
        },
    }


# ------------------------------------------------------------------ .pbit ----

DIAGRAMA = {
    "version": "1.1.0",
    "diagrams": [{
        "ordinal": 0,
        "scrollPosition": {"x": 0, "y": 0},
        "nodes": [],
        "name": "All tables",
        "zoomValue": 100,
        "pinKeyFieldsToTop": False,
        "showExtraHeaderInfo": False,
        "hideKeyFieldsWhenCollapsed": False,
        "tablesLocked": False,
    }],
    "selectedDiagram": "All tables",
    "defaultDiagram": "All tables",
}

PARTES_SEM_EXTENSAO = ["Version", "DataModelSchema", "DiagramLayout",
                       "Metadata", "Settings", "Report/Layout"]


def _content_types():
    overrides = "".join(
        '<Override PartName="/%s" ContentType="" />' % p for p in PARTES_SEM_EXTENSAO)
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="json" ContentType="" />'
        '<Default Extension="xml" ContentType="" />'
        + overrides +
        '</Types>'
    )


def escrever_pbit(destino, bim, layout):
    def utf16(texto):
        return b"\xff\xfe" + texto.encode("utf-16-le")

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _content_types().encode("utf-8"))
        z.writestr("Version", utf16("1.28"))
        z.writestr("DataModelSchema", utf16(json.dumps(bim, ensure_ascii=False, indent=2)))
        z.writestr("DiagramLayout", utf16(json.dumps(DIAGRAMA, ensure_ascii=False)))
        z.writestr("Metadata", utf16(json.dumps(
            {"Version": 3, "AutoCreatedRelationships": [], "FileDescription": NOME_MODELO},
            ensure_ascii=False)))
        z.writestr("Settings", utf16(json.dumps({"Version": 4}, ensure_ascii=False)))
        z.writestr("Report/Layout", utf16(json.dumps(layout, ensure_ascii=False)))


# ------------------------------------------------------------------ .pbip ----

def _platform(tipo, nome_exibicao):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/"
                   "platformProperties/2.0.0/schema.json",
        "metadata": {"type": tipo, "displayName": nome_exibicao},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid5(NAMESPACE, tipo + nome_exibicao))},
    }


def _escrever_json(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(dados, ensure_ascii=False, indent=2))
        f.write("\n")


def escrever_pbip(base, bim, layout):
    pasta_modelo = os.path.join(base, NOME + ".SemanticModel")
    pasta_relatorio = os.path.join(base, NOME + ".Report")
    for pasta in (pasta_modelo, pasta_relatorio):
        if os.path.isdir(pasta):
            shutil.rmtree(pasta)

    _escrever_json(os.path.join(base, NOME + ".pbip"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/pbip/"
                   "definitionProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": NOME + ".Report"}}],
        "settings": {"enableAutoRecovery": True},
    })

    _escrever_json(os.path.join(pasta_modelo, ".platform"),
                   _platform("SemanticModel", NOME_MODELO))
    _escrever_json(os.path.join(pasta_modelo, "definition.pbism"), {"version": "4.2", "settings": {}})
    _escrever_json(os.path.join(pasta_modelo, "model.bim"), bim)
    _escrever_json(os.path.join(pasta_modelo, "diagramLayout.json"), DIAGRAMA)

    _escrever_json(os.path.join(pasta_relatorio, ".platform"),
                   _platform("Report", NOME_MODELO))
    _escrever_json(os.path.join(pasta_relatorio, "definition.pbir"), {
        "version": "4.0",
        "datasetReference": {"byPath": {"path": "../" + NOME + ".SemanticModel"}},
    })
    _escrever_json(os.path.join(pasta_relatorio, "report.json"), layout)


# ----------------------------------------------------------- texto avulso ----

def escrever_texto(base):
    pasta = os.path.join(base, "modelo")
    os.makedirs(pasta, exist_ok=True)

    partes = [
        "// Consultas do Power Query (linguagem M) — modelo ControlTub / Avanço de Tubulação.",
        "// Cole cada bloco no Editor do Power Query: Nova Fonte > Consulta em Branco >",
        "// Editor Avançado. Crie primeiro o parâmetro FonteDados e a função fnCarregar.",
        "",
        "// ===== Parâmetro: FonteDados =====",
        consultas.PARAMETRO_FONTE,
        "",
        "// ===== Função: fnCarregar =====",
        consultas.FN_CARREGAR,
    ]
    for nome, texto in consultas.CONSULTAS.items():
        partes += ["", "// ===== Consulta: %s =====" % nome, texto]
    with io.open(os.path.join(pasta, "consultas.pq"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(partes) + "\n")

    linhas = [
        "// Medidas DAX — criar na tabela 'Medidas'.",
        "// Formato de exibição indicado em comentário no fim de cada medida.",
    ]
    for nome, expressao, formato, pasta_medida in modelo.MEDIDAS:
        linhas += ["", "// [%s]" % pasta_medida,
                   "%s =\n%s   // formato: %s" % (nome, expressao, formato)]
    with io.open(os.path.join(pasta, "medidas.dax"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linhas) + "\n")


def main():
    bim = construir_bim()
    layout = relatorio.construir_layout()

    escrever_pbit(os.path.join(AQUI, NOME + ".pbit"), bim, layout)
    escrever_pbip(AQUI, bim, layout)
    escrever_texto(AQUI)

    print("Tabelas .......... %d" % len(bim["model"]["tables"]))
    print("Medidas .......... %d" % len(modelo.MEDIDAS))
    print("Relacionamentos .. %d" % len(bim["model"]["relationships"]))
    print("Páginas .......... %d" % len(layout["sections"]))
    print("Gerado em ........ %s" % AQUI)


if __name__ == "__main__":
    main()
