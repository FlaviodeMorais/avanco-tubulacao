# Retomada de Fabricação e Montagem de Tubulação

Planilha para planejar a retomada do contrato: separa, dos dados do ControlTub,
o que já foi concluído (paralisação) do que ainda falta fazer, e organiza esse
restante como o **escopo novo** do contrato que recomeça em **outubro/2026**,
com **prazo de 32 meses** (até maio/2029).

## Arquivo

**`ControlTub-Retomada-Out2026.xlsx`** — 5 abas:

| Aba | Conteúdo |
|---|---|
| **Leia-me** | Explica o critério usado e o que tem em cada aba |
| **Resumo** | Cartões com os números-chave (peso concluído x remanescente, datas do contrato) + gráfico |
| **Acompanhamento_Fab_Montagem** | Escopo novo por Unidade e por Pacote SOP, e cronograma mensal (32 meses, out/26 a mai/29) pronto para preencher o avanço real mês a mês |
| **Remanescentes_Spools** | 14.055 spools sem "Liberado END" — 790,204 ton (35,4% do peso total do projeto), com todas as colunas originais da aba SGS |
| **Remanescentes_Juntas** | 52.514 juntas sem "Liberado END", de 94.585 juntas cadastradas, com todas as colunas originais da aba MAPA_JUNTA |

## Critério de "remanescente"

Um registro é remanescente quando **não tem data de Liberado END** — o mesmo
marco de conclusão que o painel web já usa (`ControlTub-Dashboard.V5.5.html`):
campo `libcdat` para spools (aba SGS), campo `dt_lib_END` para juntas (aba
MAPA_JUNTA). Sem essa data, o item nunca foi liberado — ficou parado desde a
paralisação do contrato anterior.

Os números batem exatamente com o painel publicado hoje (mesma base de dados):
peso total 2.233,721 ton, dos quais 1.443,517 ton (64,6%) já concluídos.

## Cronograma mensal — como usar

A coluna **Peso Planejado Acumulado** vem pré-preenchida com uma curva linear
(escopo novo ÷ 32) só como ponto de partida — edite para refletir o
planejamento real assim que ele existir. A coluna **Peso Realizado Acumulado**
fica em branco de propósito: preencha mês a mês conforme a obra avançar. As
colunas de % avanço e saldo já têm fórmula e recalculam sozinhas.

## Atualizar com uma exportação mais nova

Quando o ControlTub gerar uma nova extração (mesmo padrão de sempre — aba
"SGS" com cabeçalho na linha 9, aba "MAPA_JUNTA" com cabeçalho na linha 8),
rode:

```bash
python3 retomada/build_retomada.py --spools NOVO_SGS.xlsx --juntas NOVO_MAPA_JUNTA.xlsx
```

Isso gera o arquivo de novo do zero, com os números atualizados. Os arquivos
originais do ControlTub não precisam ficar no repositório — são grandes
(dezenas de MB) e são só insumo; o que importa versionar é o resultado
(`ControlTub-Retomada-Out2026.xlsx`) e o script.

Parâmetros opcionais: `--data-inicio AAAA-MM-DD` (padrão `2026-10-01`) e
`--prazo-meses N` (padrão `32`), caso o contrato mude.
