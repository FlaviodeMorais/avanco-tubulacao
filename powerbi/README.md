# Avanço de Tubulação no Power BI

Modelo do Power BI que reproduz o painel ControlTub — curva de avanço, pacotes
SOP, spools, juntas/soldadores e acabamento — lendo os **mesmos dados que o
painel publica** (`data.json` e `juntas.json`). Cada upload de planilha feito no
dashboard atualiza esses arquivos; no Power BI basta clicar em **Atualizar**.

## Por que `.pbit` e não `.pbix`

`.pbix` é um formato binário: o modelo dentro dele é um backup do motor
Analysis Services, que **só o Power BI Desktop consegue gravar**. O formato
gerável fora do Desktop é o `.pbit` (Modelo do Power BI), que carrega o modelo
inteiro (consultas, tabelas, relacionamentos, medidas e páginas) em texto.

Você abre o `.pbit` uma vez e salva como `.pbix` — daí em diante é um `.pbix`
normal.

## Passo a passo

1. Baixe **`ControlTub-Avanco-Tubulacao.pbit`** e dê dois cliques (ou, no Power
   BI Desktop: *Arquivo → Importar → Modelo do Power BI*).
2. Ele pergunta o parâmetro **`FonteDados`**. Deixe o valor sugerido
   `https://avanco-tubulacao.vercel.app` e clique em **Carregar**.
3. Na primeira carga o Power BI pede como se conectar ao site: escolha
   **Anônimo** e **Conectar**. (Se aparecer aviso de privacidade, escolha
   **Público**.)
4. Espere a carga (~17 mil spools, alguns segundos).
5. **Arquivo → Salvar como → `ControlTub - Avanço de Tubulação.pbix`**. Pronto.

Para atualizar depois: **Página Inicial → Atualizar**. Ele relê os JSON
publicados, então o Power BI acompanha o painel sem trabalho manual.

### Usar arquivos locais em vez da URL

O parâmetro `FonteDados` também aceita uma **pasta**. Use o botão *Baixar Dados
(.zip)* do painel, descompacte, e informe o caminho da pasta que contém
`data.json` e `juntas.json` — por exemplo `C:\ControlTub\dados`. Dá pra trocar
depois em *Transformar dados → Gerenciar Parâmetros*.

## Páginas do relatório

| Página | O que mostra |
|---|---|
| **Visão Geral** | Peso total, fabricado, liberado END, % concluído, curva acumulada por etapa, avanço mês a mês e pacotes SOP |
| **Por Unidade** | Matriz unidade × etapa e curva de liberado END por unidade |
| **Pacotes SOP** | Tabela de avanço por SOP e curva do pacote selecionado |
| **Spools** | Lista completa de spools com filtros de unidade e status de montagem |
| **Juntas e Soldadores** | KPIs de juntas, curva acumulada, índice de reparo por diâmetro e ranking de soldadores |
| **Materiais e Acabamento** | Fabricado por material, tempo médio, pintura/isolamento/STH e ranking de linhas |

## Modelo de dados

Esquema estrela com dimensões `Meses`, `Etapas`, `Unidades`, `Materiais` e
`Ranking_SOP`, e fatos `Avanco_Unidade`, `Avanco_SOP`, `Spools`,
`Material_Fabricado`, `Juntas_Curva` e `Juntas_Material`.

Duas convenções importantes, herdadas do painel:

- As curvas são **acumuladas** (peso, em toneladas, cuja data da etapa é menor
  ou igual ao fim daquele mês). Por isso as medidas de posição atual
  (`Fabricado (ton)`, `Liberado END (ton)`, …) fixam o **último mês visível** em
  vez de somar meses — somar uma curva acumulada contaria o mesmo peso 24 vezes.
- A janela é de **24 meses**, a mesma do painel.

As 35 medidas ficam na tabela `Medidas`, agrupadas em pastas (Escopo, Avanço,
Posição atual, SOP, Material, Juntas, Acabamento).

## Se o `.pbit` não abrir

O `.pbit` foi montado e validado fora do Power BI (estrutura do pacote,
consultas conferidas contra os dados reais, e todas as referências dos visuais
resolvidas no modelo), mas **não foi aberto no Power BI Desktop** — não há
Desktop no ambiente onde ele é gerado. Se sua versão reclamar do arquivo, há
três alternativas, em ordem de esforço:

1. **Projeto `.pbip`** — abra `ControlTub-Avanco-Tubulacao.pbip` no Power BI
   Desktop. É o mesmo modelo e o mesmo relatório, no formato de pastas
   (requer Desktop de 2024 em diante).
2. **Montar à mão** — `modelo/consultas.pq` traz cada consulta M pronta para
   colar em *Nova Fonte → Consulta em Branco → Editor Avançado*, e
   `modelo/medidas.dax` traz as medidas. Crie primeiro o parâmetro `FonteDados`
   e a função `fnCarregar`; o resto depende só deles.
3. **Direto da planilha** — *Obter Dados → Excel* apontando para
   `ControlTub_Planilha_Formulas.xlsx` na raiz do repositório. As abas `Dados`,
   `Curva_Avanco_Rundown`, `Avanco_SOP`, `Ranking_Soldadores`, `KPIs` e
   `Ranking_Linhas` já vêm tabuladas. Você monta os visuais, mas não precisa de
   nenhuma transformação.

## Regenerar os arquivos

```bash
python3 powerbi/build_pbit.py
```

As definições ficam em três arquivos, que são a fonte da verdade:

- `consultas.py` — consultas do Power Query (M)
- `modelo.py` — tabelas, colunas, medidas DAX e relacionamentos
- `relatorio.py` — páginas e visuais

O script gera o `.pbit`, o projeto `.pbip` e os textos em `modelo/`. Não edite
`modelo/consultas.pq` nem `modelo/medidas.dax` à mão: eles são saída.
