// Azure Function (HTTP, authLevel "function") — proxy seguro para publicar
// data.json/juntas.json no repositório do GitHub Pages.
//
// Por que existe: o dashboard é um site 100% estático (GitHub Pages), sem
// servidor próprio. Pra permitir que VÁRIAS pessoas do time publiquem uma
// atualização sem que cada uma precise de um token de escrita do GitHub,
// o token fica guardado só aqui (variável de ambiente "GITHUB_TOKEN" desta
// Function App) — nunca no navegador de quem usa o painel. O acesso a esta
// Function é controlado pela "function key" do Azure (Application Settings
// > Function Keys), que é a senha compartilhada com o time.
//
// Requer Node.js 18+ na Function App (usa fetch() nativo).

const GH_OWNER = 'FlaviodeMorais';
const GH_REPO = 'avanco-tubulacao';
const GH_BRANCH = 'main';

async function githubPutFile(path, contentObj, message, token) {
  const api = `https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/contents/${path}`;
  const headers = {
    'Authorization': 'Bearer ' + token,
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'controltub-publish-function',
  };

  const getRes = await fetch(`${api}?ref=${GH_BRANCH}`, { headers });
  let sha;
  if (getRes.status === 200) {
    sha = (await getRes.json()).sha;
  } else if (getRes.status !== 404) {
    throw new Error(`Falha ao ler ${path} no GitHub: HTTP ${getRes.status}`);
  }

  const contentB64 = Buffer.from(JSON.stringify(contentObj)).toString('base64');
  const putRes = await fetch(api, {
    method: 'PUT',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, content: contentB64, branch: GH_BRANCH, sha }),
  });
  if (!putRes.ok) {
    throw new Error(`Falha ao gravar ${path} no GitHub: HTTP ${putRes.status}`);
  }
  return putRes.json();
}

module.exports = async function (context, req) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    context.res = { status: 500, body: { error: 'GITHUB_TOKEN não configurado nas Application Settings desta Function App.' } };
    return;
  }

  const body = req.body || {};
  const { data, juntas } = body;
  if (!data && !juntas) {
    context.res = { status: 400, body: { error: 'Envie "data" e/ou "juntas" no corpo da requisição (JSON).' } };
    return;
  }

  const msg = `Atualiza dados via painel — ${new Date().toISOString()}`;
  const results = {};
  try {
    if (data) { await githubPutFile('data.json', data, msg, token); results.data = 'ok'; }
    if (juntas) { await githubPutFile('juntas.json', juntas, msg, token); results.juntas = 'ok'; }
  } catch (err) {
    context.log.error(err);
    context.res = { status: 502, body: { error: err.message } };
    return;
  }

  context.res = { status: 200, body: { ok: true, results } };
};
