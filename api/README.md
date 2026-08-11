# `/api/publish` — publica data.json/juntas.json sem token individual

O dashboard e esta Function rodam juntos, na mesma origem
(`avanco-tubulacao.vercel.app`) — o único link oficial do painel a partir de
agora. Por rodarem juntos, não precisa de CORS nem de nada especial: o
navegador chama `/api/publish` (caminho relativo) direto.

Resolve o problema de sempre: pra permitir que várias pessoas publiquem uma
atualização sem que cada uma precise do próprio token de escrita do GitHub,
**só esta Function** guarda um token (variável de ambiente na Vercel, nunca
no navegador de ninguém); o time usa uma chave compartilhada (`PUBLISH_KEY`)
pra chamar.

Custo: plano gratuito da Vercel cobre isso tranquilamente.

## Passo a passo

### 1. Variáveis de ambiente (o passo que travou da última vez)
No projeto na Vercel → **Settings** → **Environment Variables** → adicione:

- `GITHUB_TOKEN` → um token criado em
  **github.com/settings/personal-access-tokens/new**, com
  **Repository access → Only select repositories → avanco-tubulacao** e
  **Permissions → Contents → Read and write**.
- `PUBLISH_KEY` → qualquer texto forte que vai servir de senha do time.

**Importante**: ao adicionar cada variável, confira que o ambiente
**"Production"** está marcado (não só Preview/Development) — é o que faz o
site publicado de verdade (`avanco-tubulacao.vercel.app`) enxergar a
variável. Depois de salvar, vá em **Deployments** → deployment mais recente
→ **⋯** → **Redeploy** (variável de ambiente só vale a partir de um novo
deploy).

### 2. Usar
No dashboard, clique em **"Baixar Dados" → Publicar agora** (ou o texto que
estiver no botão) — ele pede a **chave** (`PUBLISH_KEY`) uma vez, num campo
na própria tela, e salva só naquele navegador.

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
- A chave (`PUBLISH_KEY`) é a credencial de quem pode publicar — trate como
  senha: não publique em lugar público, não compartilhe fora do time. Pra
  revogar, troque `PUBLISH_KEY` nas variáveis de ambiente do projeto e
  redistribua a chave nova.
