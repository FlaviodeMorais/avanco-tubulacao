# Function "PublicarDados" — publica data.json/juntas.json sem token individual

Esta função existe pra resolver um problema: o dashboard é um site estático
(GitHub Pages), sem servidor próprio. Sem ela, cada pessoa que quisesse
publicar uma atualização precisaria do próprio token de escrita do GitHub —
ruim de gerenciar com várias pessoas. Com a função, **só ela** guarda um
token (nas Application Settings, nunca no navegador de ninguém); o time usa
uma "function key" (senha compartilhada, gerada pelo Azure) pra chamar.

Custo: plano Consumption do Azure Functions tem 1 milhão de execuções/mês
grátis (permanente, não é trial) — um botão clicado algumas vezes por dia
fica muito abaixo disso.

## Passo a passo (tudo pelo portal, sem precisar instalar nada no PC)

### 1. Criar a Function App
1. Acesse **portal.azure.com** → **Criar um recurso** → busque **"Function App"** → Criar.
2. Preencha:
   - **Nome**: algo único, ex. `controltub-publicar` (vira parte da URL).
   - **Publicar**: Código
   - **Pilha de runtime**: **Node.js**
   - **Versão**: **18 LTS** (ou mais nova) — a função usa `fetch()` nativo, precisa de Node 18+.
   - **Região**: a mais próxima (ex. Brazil South).
   - **Plano de hospedagem**: **Consumo (Serverless)**.
3. Criar (o Azure cria junto uma Storage Account — normal, faz parte do Functions).
4. Espere o deploy terminar (~1-2 min) e abra o recurso criado.

### 2. Criar a função HTTP dentro dela
1. No menu lateral da Function App → **Funções** → **Criar**.
2. **Ambiente de desenvolvimento**: **Desenvolver no portal**.
3. Modelo: **HTTP trigger**.
4. **Nome da função**: `PublicarDados`.
5. **Nível de autorização**: **Função** (Function).
6. Criar.

### 3. Colar o código
1. Abra a função `PublicarDados` → **Código + Teste**.
2. Apague o conteúdo padrão de `index.js` e cole o conteúdo de
   [`PublicarDados/index.js`](PublicarDados/index.js) deste repositório.
3. **Salvar**.

### 4. Configurar o token do GitHub (só aqui, uma vez)
1. Crie um token em **github.com/settings/personal-access-tokens/new**:
   - Repository access → Only select repositories → `avanco-tubulacao`
   - Permissions → Contents → **Read and write**
2. Na Function App → **Configuração** → **Application settings** → **Novo item**:
   - Nome: `GITHUB_TOKEN`
   - Valor: (cole o token)
3. **Salvar** (a Function App reinicia).

### 5. Liberar o navegador (CORS)
1. Na Function App → **CORS** (menu lateral, em API).
2. Adicione as origens permitidas:
   - `https://flaviodemorais.github.io`
   - `http://localhost:5500` (pra testar local)
3. **Salvar**.

### 6. Pegar a URL da função
1. Na função `PublicarDados` → **Obter URL da Função** (ícone no topo).
2. Copie a URL completa (já vem com `?code=...` — essa é a senha
   compartilhada do time; qualquer um com essa URL completa consegue publicar).
3. Cole essa URL no dashboard quando ele pedir (primeira vez que clicar em
   "Publicar agora" após esta migração) — fica salva só naquele navegador.

## Segurança

- O `GITHUB_TOKEN` nunca sai desta Function App — não fica em nenhum
  navegador, não fica no código do dashboard.
- A URL completa da função (com `?code=`) é a credencial de quem pode
  publicar — trate como uma senha: não publique em lugar público, não
  compartilhe fora do time. Pra revogar, gere uma nova key em
  **Function App → Chaves de função** e distribua a URL nova pro time.
