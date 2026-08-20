# -*- coding: utf-8 -*-
"""Consultas em linguagem M (Power Query) do modelo ControlTub.

Cada entrada é uma consulta do Power Query. O texto aqui é a fonte da verdade:
`build_pbit.py` embute estas consultas nas partições do modelo (.pbit/.pbip) e
também as exporta para `modelo/consultas.pq`, para quem preferir colar à mão no
Editor do Power Query.
"""

# Parâmetro: aceita a URL do painel publicado (atualiza sozinho) ou uma pasta
# local contendo data.json e juntas.json.
PARAMETRO_FONTE = (
    '"https://avanco-tubulacao.vercel.app" '
    'meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
)

FN_CARREGAR = r'''let
    fnCarregar = (arquivo as text) as record =>
        let
            Conteudo =
                if Text.StartsWith(Text.Lower(FonteDados), "http")
                then Web.Contents(FonteDados, [RelativePath = arquivo])
                else File.Contents(
                    FonteDados
                    & (if Text.EndsWith(FonteDados, "\") then "" else "\")
                    & arquivo
                ),
            Documento = Json.Document(Conteudo, 65001)
        in
            Documento
in
    fnCarregar'''

CONSULTAS = {}

CONSULTAS["Meses"] = r'''let
    Dados = fnCarregar("data.json"),
    Abreviacoes = {"Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"},
    Tabela = Table.FromList(Dados[months], Splitter.SplitByNothing(), {"Mes"}, null, ExtraValues.Error),
    ComOrdem = Table.AddIndexColumn(Tabela, "Ordem", 1, 1, Int64.Type),
    ComFimDoMes = Table.AddColumn(ComOrdem, "FimDoMes", each
        let
            Partes = Text.Split([Mes], "/"),
            NumeroMes = List.PositionOf(Abreviacoes, Partes{0}) + 1,
            Ano = 2000 + Number.FromText(Partes{1})
        in
            Date.EndOfMonth(#date(Ano, NumeroMes, 1)), type date),
    ComAno = Table.AddColumn(ComFimDoMes, "Ano", each Date.Year([FimDoMes]), Int64.Type),
    ComMesNum = Table.AddColumn(ComAno, "MesNum", each Date.Month([FimDoMes]), Int64.Type),
    Tipos = Table.TransformColumnTypes(ComMesNum, {{"Mes", type text}})
in
    Tipos'''

CONSULTAS["Etapas"] = r'''let
    Dados = fnCarregar("data.json"),
    Tabela = Table.FromList(Dados[stages], Splitter.SplitByNothing(), {"Etapa"}, null, ExtraValues.Error),
    ComOrdem = Table.AddIndexColumn(Tabela, "OrdemEtapa", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ComOrdem, {{"Etapa", type text}})
in
    Tipos'''

CONSULTAS["Unidades"] = r'''let
    Dados = fnCarregar("data.json"),
    Tabela = Table.FromList(Dados[unidades], Splitter.SplitByNothing(), {"Unidade"}, null, ExtraValues.Error),
    Tipos = Table.TransformColumnTypes(Tabela, {{"Unidade", type text}})
in
    Tipos'''

CONSULTAS["Materiais"] = r'''let
    Dados = fnCarregar("data.json"),
    Tabela = Table.FromList(Dados[materiais], Splitter.SplitByNothing(), {"Material"}, null, ExtraValues.Error),
    Tipos = Table.TransformColumnTypes(Tabela, {{"Material", type text}})
in
    Tipos'''

# by_unidade: { unidade -> { total, series: { etapa -> [24 valores acumulados em ton] } } }
CONSULTAS["Avanco_Unidade"] = r'''let
    Dados = fnCarregar("data.json"),
    PorUnidade = Dados[by_unidade],
    Unidades = Record.FieldNames(PorUnidade),
    Linhas = List.Combine(List.Transform(Unidades, (u) =>
        let
            Series = Record.Field(PorUnidade, u)[series],
            Etapas = Record.FieldNames(Series)
        in
            List.Combine(List.Transform(Etapas, (e) =>
                let Valores = Record.Field(Series, e) in
                List.Transform(List.Positions(Valores), (i) => {u, e, i + 1, Valores{i}})
            ))
    )),
    Tabela = Table.FromRows(Linhas, {"Unidade", "Etapa", "Ordem", "Ton_Acumulado"}),
    Tipos = Table.TransformColumnTypes(Tabela, {
        {"Unidade", type text}, {"Etapa", type text},
        {"Ordem", Int64.Type}, {"Ton_Acumulado", type number}})
in
    Tipos'''

CONSULTAS["Avanco_SOP"] = r'''let
    Dados = fnCarregar("data.json"),
    PorSOP = Dados[by_sop],
    Pacotes = Record.FieldNames(PorSOP),
    Linhas = List.Combine(List.Transform(Pacotes, (s) =>
        let
            Series = Record.Field(PorSOP, s)[series],
            Etapas = Record.FieldNames(Series)
        in
            List.Combine(List.Transform(Etapas, (e) =>
                let Valores = Record.Field(Series, e) in
                List.Transform(List.Positions(Valores), (i) => {s, e, i + 1, Valores{i}})
            ))
    )),
    Tabela = Table.FromRows(Linhas, {"SOP", "Etapa", "Ordem", "Ton_Acumulado"}),
    Tipos = Table.TransformColumnTypes(Tabela, {
        {"SOP", type text}, {"Etapa", type text},
        {"Ordem", Int64.Type}, {"Ton_Acumulado", type number}})
in
    Tipos'''

# records: [iso, spool, linha, unidade, peso_kg, cod_status_fab, cod_status_mon]
CONSULTAS["Spools"] = r'''let
    Dados = fnCarregar("data.json"),
    MapaFab = Dados[status_fab],
    MapaMon = Dados[status_mon],
    Tabela = Table.FromRows(Dados[records], {
        "ISO", "Spool", "Linha", "Unidade", "Peso_kg", "CodStatusFab", "CodStatusMon"}),
    ComStatusFab = Table.AddColumn(Tabela, "Status Fabricacao", each
        let Achados = List.Select(MapaFab, (s) => Text.StartsWith(s, [CodStatusFab]))
        in if List.Count(Achados) > 0 then Achados{0} else [CodStatusFab], type text),
    ComStatusMon = Table.AddColumn(ComStatusFab, "Status Montagem", each
        let Achados = List.Select(MapaMon, (s) => Text.StartsWith(s, [CodStatusMon]))
        in if List.Count(Achados) > 0 then Achados{0} else [CodStatusMon], type text),
    ComTon = Table.AddColumn(ComStatusMon, "Peso_ton", each [Peso_kg] / 1000, type number),
    Tipos = Table.TransformColumnTypes(ComTon, {
        {"ISO", type text}, {"Spool", type text}, {"Linha", type text}, {"Unidade", type text},
        {"Peso_kg", type number}, {"CodStatusFab", type text}, {"CodStatusMon", type text}})
in
    Tipos'''

CONSULTAS["Ranking_SOP"] = r'''let
    Dados = fnCarregar("data.json"),
    Tabela = Table.FromRecords(Dados[sop_ranking]),
    Renomeada = Table.RenameColumns(Tabela, {
        {"sop", "SOP"}, {"linhas", "Linhas"}, {"sths", "STHs"}, {"spools", "Spools"},
        {"peso_total", "Peso Total (ton)"}, {"peso_fabricado", "Peso Fabricado (ton)"},
        {"peso_liberado", "Peso Liberado (ton)"},
        {"pct_fabricado", "% Fabricado"}, {"pct_liberado", "% Liberado"}}),
    Tipos = Table.TransformColumnTypes(Renomeada, {
        {"SOP", type text}, {"Linhas", Int64.Type}, {"STHs", Int64.Type}, {"Spools", Int64.Type},
        {"Peso Total (ton)", type number}, {"Peso Fabricado (ton)", type number},
        {"Peso Liberado (ton)", type number},
        {"% Fabricado", type number}, {"% Liberado", type number}})
in
    Tipos'''

CONSULTAS["Ranking_Linhas"] = r'''let
    Dados = fnCarregar("data.json"),
    Tabela = Table.FromRecords(Dados[linhas_ranking]),
    Renomeada = Table.RenameColumns(Tabela, {
        {"linha", "Linha"}, {"spools", "Spools"},
        {"peso_total", "Peso Total (ton)"}, {"peso_liberado", "Peso Liberado (ton)"},
        {"pct_liberado", "% Liberado"}}),
    Tipos = Table.TransformColumnTypes(Renomeada, {
        {"Linha", type text}, {"Spools", Int64.Type},
        {"Peso Total (ton)", type number}, {"Peso Liberado (ton)", type number},
        {"% Liberado", type number}})
in
    Tipos'''

CONSULTAS["Material_Fabricado"] = r'''let
    Dados = fnCarregar("data.json"),
    PorMaterial = Dados[fabricado_por_material],
    Materiais = Record.FieldNames(PorMaterial),
    Linhas = List.Combine(List.Transform(Materiais, (m) =>
        let Valores = Record.Field(PorMaterial, m) in
        List.Transform(List.Positions(Valores), (i) => {m, i + 1, Valores{i}}))),
    Tabela = Table.FromRows(Linhas, {"Material", "Ordem", "Ton_Fabricado_Acumulado"}),
    Tipos = Table.TransformColumnTypes(Tabela, {
        {"Material", type text}, {"Ordem", Int64.Type}, {"Ton_Fabricado_Acumulado", type number}})
in
    Tipos'''

# Junta o tempo medio de fabricacao (data.json) com o de soldagem (juntas.json).
CONSULTAS["Tempo_Medio"] = r'''let
    Dados = fnCarregar("data.json"),
    Juntas = fnCarregar("juntas.json"),
    Fabricacao = let R = Dados[tempo_medio_fabricacao_material] in
        List.Transform(Record.FieldNames(R), (m) =>
            {m, "Fabricacao", Record.Field(R, m)[dias], Record.Field(R, m)[n]}),
    Soldagem = let R = Juntas[tempo_medio_soldagem_material] in
        List.Transform(Record.FieldNames(R), (m) =>
            {m, "Soldagem", Record.Field(R, m)[dias], Record.Field(R, m)[n]}),
    Tabela = Table.FromRows(Fabricacao & Soldagem, {"Material", "Tipo", "Dias", "Amostra"}),
    Tipos = Table.TransformColumnTypes(Tabela, {
        {"Material", type text}, {"Tipo", type text},
        {"Dias", type number}, {"Amostra", Int64.Type}})
in
    Tipos'''

CONSULTAS["KPIs"] = r'''let
    Dados = fnCarregar("data.json"),
    Tabela = Table.FromRecords({Dados[kpis]}),
    Renomeada = Table.RenameColumns(Tabela, {
        {"total_ton", "Peso Total (ton)"}, {"total_spools", "Spools (qtd)"},
        {"nao_iniciados", "Spools Nao Iniciados"}, {"nao_iniciados_ton", "Nao Iniciados (ton)"},
        {"sop_total_n", "Pacotes SOP"}, {"sop_avg_pct", "% Medio Avanco SOP"},
        {"sop_completos", "SOPs Concluidos"}, {"sop_prontos_ton", "SOP Liberado (ton)"},
        {"sth_total_n", "Sistemas STH"}, {"sth_iniciados_n", "STH Iniciados"},
        {"sth_completos_n", "STH Concluidos"}, {"sth_pct_peso", "% Peso com STH"},
        {"pintura_area_previsto", "Pintura Prevista (m2)"},
        {"pintura_area_realizado", "Pintura Realizada (m2)"}, {"pintura_pct", "% Pintura"},
        {"isolamento_area_previsto", "Isolamento Previsto (m2)"},
        {"isolamento_area_realizado", "Isolamento Realizado (m2)"},
        {"isolamento_pct", "% Isolamento"},
        {"spoolsAc2_previsto_ton", "AC ate 2pol Previsto (ton)"},
        {"spoolsAc2_realizado_ton", "AC ate 2pol Realizado (ton)"},
        {"spoolsAc2_pct", "% AC ate 2pol"}}, MissingField.Ignore),
    Tipos = Table.TransformColumnTypes(Renomeada,
        List.Transform(Table.ColumnNames(Renomeada), (c) => {c, type number}))
in
    Tipos'''

CONSULTAS["Juntas_KPIs"] = r'''let
    Juntas = fnCarregar("juntas.json"),
    Tabela = Table.FromRecords({Juntas[kpis]}),
    Renomeada = Table.RenameColumns(Tabela, {
        {"total_juntas", "Juntas (total)"}, {"soldadas", "Soldadas"},
        {"lib_end", "Liberadas END"}, {"com_vs", "Com Visual de Solda"},
        {"com_end_ensaio", "Com Ensaio END"},
        {"reparos1", "Reparos 1a"}, {"reparos2", "Reparos 2a"},
        {"pct_soldadas", "% Soldadas"}, {"pct_lib_end", "% Liberadas END"},
        {"pct_reparo", "% Reparo"},
        {"end_rx_total", "END RX Previsto"}, {"end_us_total", "END US Previsto"},
        {"end_rx_ok", "END RX Realizado"}, {"end_us_ok", "END US Realizado"}},
        MissingField.Ignore),
    Tipos = Table.TransformColumnTypes(Renomeada,
        List.Transform(Table.ColumnNames(Renomeada), (c) => {c, type number}))
in
    Tipos'''

CONSULTAS["Soldadores"] = r'''let
    Juntas = fnCarregar("juntas.json"),
    Tabela = Table.FromRecords(Juntas[soldadores]),
    Renomeada = Table.RenameColumns(Tabela, {
        {"soldador", "Soldador"}, {"total", "Juntas"}, {"soldadas", "Soldadas"},
        {"reparos", "Reparos"}, {"reparos2", "Reparos 2a"}, {"lib_end", "Liberadas END"},
        {"pct_reparo", "% Reparo"}, {"pct_conclusao", "% Conclusao"}}),
    Tipos = Table.TransformColumnTypes(Renomeada, {
        {"Soldador", type text}, {"Juntas", Int64.Type}, {"Soldadas", Int64.Type},
        {"Reparos", Int64.Type}, {"Reparos 2a", Int64.Type}, {"Liberadas END", Int64.Type},
        {"% Reparo", type number}, {"% Conclusao", type number}})
in
    Tipos'''

CONSULTAS["Reparos_Diametro"] = r'''let
    Juntas = fnCarregar("juntas.json"),
    Tabela = Table.FromRecords(Juntas[reparos_por_diam]),
    Renomeada = Table.RenameColumns(Tabela, {
        {"pol", "Diametro"}, {"total", "Juntas"}, {"reparos", "Reparos"}, {"pct", "% Reparo"}}),
    Tipos = Table.TransformColumnTypes(Renomeada, {
        {"Diametro", type text}, {"Juntas", Int64.Type},
        {"Reparos", Int64.Type}, {"% Reparo", type number}})
in
    Tipos'''

CONSULTAS["Juntas_Curva"] = r'''let
    Juntas = fnCarregar("juntas.json"),
    Meses = Juntas[curve_months],
    Soldadas = List.Transform(List.Positions(Meses), (i) => {Meses{i}, "Soldadas", Juntas[curve_sold]{i}}),
    Liberadas = List.Transform(List.Positions(Meses), (i) => {Meses{i}, "Liberadas END", Juntas[curve_lib]{i}}),
    Tabela = Table.FromRows(Soldadas & Liberadas, {"Mes", "Serie", "Juntas"}),
    Tipos = Table.TransformColumnTypes(Tabela, {
        {"Mes", type text}, {"Serie", type text}, {"Juntas", Int64.Type}})
in
    Tipos'''

CONSULTAS["Juntas_Material"] = r'''let
    Juntas = fnCarregar("juntas.json"),
    Meses = Juntas[curve_months],
    PorMaterial = Juntas[curve_sold_material],
    Materiais = Record.FieldNames(PorMaterial),
    Linhas = List.Combine(List.Transform(Materiais, (m) =>
        let Valores = Record.Field(PorMaterial, m) in
        List.Transform(List.Positions(Valores), (i) => {Meses{i}, m, Valores{i}}))),
    Tabela = Table.FromRows(Linhas, {"Mes", "Material", "Juntas Soldadas"}),
    Tipos = Table.TransformColumnTypes(Tabela, {
        {"Mes", type text}, {"Material", type text}, {"Juntas Soldadas", Int64.Type}})
in
    Tipos'''

# Tabela vazia que hospeda todas as medidas DAX.
CONSULTAS["Medidas"] = r'''let
    Tabela = #table(type table [Coluna = Int64.Type], {{1}})
in
    Tabela'''
