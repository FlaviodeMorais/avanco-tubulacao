# `/api/publish` — publica data.json/juntas.json sem token individual

Resolve o mesmo problema de antes: o dashboard é um site estático (GitHub
Pages), sem servidor próprio. Sem isso, cada pessoa que quisesse publicar uma
atualização precisaria do próprio token de escrita do GitHub — ruim de
gerenciar com várias pessoas. Com esta Function, **só ela** guarda um token
(variável de ambiente na Vercel, nunca no navegador de ninguém); o time usa
uma chave compartilhada (`PUBLISH_KEY`) pra chamar.

Custo: plano gratuito da Vercel cobre isso tranquilamente (uso muito abaixo
de qualquer limite do free tier).

## Passo a passo

### 1. Conectar o repositório na Vercel
1. Acesse **vercel.com** → **Continue with GitHub** (usa a mesma conta do
   GitHub que já tem acesso a este repositório — não precisa criar usuário novo).
2. **Add New…** → **Project** → selecione o repositório `avanco-tubulacao`
   → **Import**.
3. Em **Framework Preset**, deixe **Other** (não é Next.js/React — é site
   estático + esta function).
4. **Antes de clicar em Deploy**, expanda **Environment Variables** e adicione:
   - `GITHUB_TOKEN` → um token criado em
     **github.com/settings/personal-access-tokens/new**, com
     **Repository access → Only select repositories → avanco-tubulacao** e
     **Permissions → Contents → Read and write**.
   - `PUBLISH_KEY` → qualquer texto forte que vai servir de senha do time
     (ex. gere uma string aleatória longa).
5. **Deploy**.

### 2. Conferir a URL do projeto
1. Depois do deploy, a Vercel mostra a URL do projeto — algo como
   `https://avanco-tubulacao.vercel.app` (pode vir com um sufixo se o nome
   já estiver em uso).
2. Essa URL já está fixada no código do dashboard
   (`PUBLISH_ENDPOINT` em `ControlTub-Dashboard.V5.5.html`). Se o nome do
   projeto na Vercel vier diferente de `avanco-tubulacao`, atualize essa
   constante pra bater com a URL real.
3. No dashboard, clique em **"Baixar Dados" → Publicar agora** — ele só pede
   a **chave** (o valor de `PUBLISH_KEY`, não a URL inteira), num campo na
   própria tela. Fica salva só naquele navegador.

## Detalhes

- Cada push no repositório (inclusive os commits que esta própria function
  faz ao publicar) dispara um redeploy automático na Vercel — é esperado,
  não afeta o GitHub Pages nem o funcionamento do botão.
- CORS já está liberado no código só para `flaviodemorais.github.io` e
  `localhost:5500` (teste local). Pra outro domínio, edite `ALLOWED_ORIGINS`
  em `publish.js`.

## Segurança

- O `GITHUB_TOKEN` nunca sai desta Function — não fica em nenhum navegador,
  não fica no código do dashboard.
- A chave (`PUBLISH_KEY`) é a credencial de quem pode publicar — trate como
  senha: não publique em lugar público, não compartilhe fora do time. Pra
  revogar, troque `PUBLISH_KEY` nas variáveis de ambiente do projeto
  (Vercel → Settings → Environment Variables) e redistribua a chave nova.
