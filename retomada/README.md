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

## Levar isso pro painel web (avanco-tubulacao.vercel.app)

O painel já sabe ler o formato bruto do ControlTub (mesma aba "SGS"/"MAPA_JUNTA"
que ele sempre aceitou) — então dá pra publicar a retomada nele com o upload de
sempre, subindo as abas **Remanescentes_Spools** e **Remanescentes_Juntas**
desta planilha (salvando cada uma como um `.xlsx` avulso com a aba renomeada
para `SGS` / `MAPA_JUNTA`, no mesmo padrão do arquivo original).

Só tem uma pegadinha: como remanescente por definição não tem data de "Liberado
END", e boa parte também não tem NENHUMA data ainda nas outras etapas, o painel
detectaria uma janela de tempo sem sentido (ou vazia) se não soubesse que esse é
um recomeço com data e prazo contratual próprios. Por isso o painel agora tem
uma opção **"Janela de Retomada"** no topo (ao lado de "Sistema/Unidade"):

1. Marque **Ativar**, preencha **Início** (`01/10/2026`) e **Prazo** (`32` meses).
2. Depois disso, suba o `.xlsx` de Remanescentes normalmente pelo botão
   "Mapa de Spools ou Juntas". O gráfico passa a mostrar exatamente a janela
   out/2026 → mai/2029, mesmo que ainda não exista nenhum dado real nesse
   período — e, se o trabalho real avançar além do prazo, o painel estende a
   janela sozinho pra mostrar o atraso em vez de cortar o gráfico.
3. Essa opção só vale a partir do **próximo upload** — não altera o que já
   está publicado hoje, e fica desligada por padrão pra quem não mexer nela
   (comportamento do painel 100% igual ao de sempre).
