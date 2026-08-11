# `/api/publish` — publica data.json/juntas.json sem token individual

O dashboard e esta Function rodam juntos, na mesma origem
(`avanco-tubulacao.vercel.app`) — o único link oficial do painel a partir de
agora. `vercel.json` reescreve `/` para servir o
`ControlTub-Dashboard.V5.5.html` (a URL continua sendo a raiz, sem redirect
visível). Por rodarem juntos, não precisa de CORS nem de nada especial: o
navegador chama `/api/publish` (caminho relativo) direto.

Resolve o problema de sempre: pra permitir que qualquer pessoa publique uma
atualização sem precisar do próprio token de escrita do GitHub, **só esta
Function** guarda um token (variável de ambiente na Vercel, nunca no
navegador de ninguém).

**Sem chave/senha nesta rota.** Isso é intencional — todo upload de planilha
bem-sucedido chama esta rota automaticamente (ver "Como é usado" abaixo), sem
pedir nada a quem está usando o painel. Ou seja: quem tiver acesso ao link do
painel e fizer um upload consegue publicar. Se algum dia isso deixar de ser
aceitável (ex.: o link circular fora do time), é preciso reintroduzir algum
controle de acesso aqui.

Custo: plano gratuito da Vercel cobre isso tranquilamente.

## Passo a passo

### 1. Variável de ambiente (o passo que travou da última vez)
No projeto na Vercel → **Settings** → **Environment Variables** → adicione:

- `GITHUB_TOKEN` → um token criado em
  **github.com/settings/personal-access-tokens/new**, com
  **Repository access → Only select repositories → avanco-tubulacao** e
  **Permissions → Contents → Read and write**.

**Importante**: ao adicionar a variável, confira que o ambiente
**"Production"** está marcado (não só Preview/Development) — é o que faz o
site publicado de verdade (`avanco-tubulacao.vercel.app`) enxergar a
variável. Depois de salvar, vá em **Deployments** → deployment mais recente
→ **⋯** → **Redeploy** (variável de ambiente só vale a partir de um novo
deploy).

### 2. Como é usado
Não tem botão de "publicar" separado. No dashboard, ao fazer upload de um
Mapa de Spools ou de Juntas (.xlsx), o painel recalcula os dados, salva no
navegador de quem fez o upload (como sempre) **e chama esta rota
automaticamente** — em ~1 min todos que abrirem o link veem a mesma
atualização. Se a publicação falhar (ex.: token não configurado), o upload
local não é desfeito — só aparece um aviso dizendo que a publicação não
aconteceu dessa vez.

O botão **"Baixar Dados (.zip)"** é outra coisa: baixa `data.json` +
`juntas.json` compactados só pra guardar localmente (ex.: uma futura
migração pra BI) — não chama esta rota, não publica nada.

## Detalhes

- Cada push no repositório (inclusive os commits que esta própria function
  faz ao publicar) dispara um redeploy automático na Vercel — esperado, não
  afeta nada.
- Sem CORS porque front e back são same-origin — se um dia o dashboard for
  acessado de outro domínio além de `avanco-tubulacao.vercel.app`, essa
  chamada vai falhar (por design, não é bug).

## Segurança

- O `GITHUB_TOKEN` nunca sai desta Function — não fica em nenhum navegador,
  não fica no código do dashboard.
- Não há autenticação nesta rota: qualquer requisição `POST /api/publish`
  que chegar (do painel ou de qualquer outro lugar) vai gravar
  `data.json`/`juntas.json` no repositório. É uma troca deliberada de
  segurança por simplicidade — ver seção acima.
