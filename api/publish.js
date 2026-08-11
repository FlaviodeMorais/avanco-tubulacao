// Vercel Serverless Function — proxy seguro para publicar data.json/juntas.json
// no repositório do GitHub Pages.
//
// Por que existe: o dashboard é um site 100% estático (GitHub Pages), sem
// servidor próprio. Pra permitir que VÁRIAS pessoas do time publiquem uma
// atualização sem que cada uma precise de um token de escrita do GitHub, o
// token fica guardado só aqui (variável de ambiente "GITHUB_TOKEN" deste
// projeto na Vercel) — nunca no navegador de quem usa o painel. O acesso é
// controlado por uma chave compartilhada (variável "PUBLISH_KEY"), enviada
// pelo dashboard como ?key=... na URL.

const GH_OWNER = 'FlaviodeMorais';
const GH_REPO = 'avanco-tubulacao';
const GH_BRANCH = 'main';

const ALLOWED_ORIGINS = [
  'https://flaviodemorais.github.io',
  'http://localhost:5500',
];

function setCors(req, res) {
  const origin = req.headers.origin;
  if (ALLOWED_ORIGINS.includes(origin)) res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

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

module.exports = async (req, res) => {
  setCors(req, res);
  if (req.method === 'OPTIONS') { res.status(204).end(); return; }
  if (req.method !== 'POST') { res.status(405).json({ error: 'Use POST.' }); return; }

  const expectedKey = process.env.PUBLISH_KEY;
  const givenKey = req.query.key;
  if (!expectedKey) { res.status(500).json({ error: 'PUBLISH_KEY não configurada nas variáveis de ambiente do projeto.' }); return; }
  if (givenKey !== expectedKey) { res.status(401).json({ error: 'Chave inválida.' }); return; }

  const token = process.env.GITHUB_TOKEN;
  if (!token) { res.status(500).json({ error: 'GITHUB_TOKEN não configurado nas variáveis de ambiente do projeto.' }); return; }

  const { data, juntas } = req.body || {};
  if (!data && !juntas) { res.status(400).json({ error: 'Envie "data" e/ou "juntas" no corpo (JSON).' }); return; }

  const msg = `Atualiza dados via painel — ${new Date().toISOString()}`;
  const results = {};
  try {
    if (data) { await githubPutFile('data.json', data, msg, token); results.data = 'ok'; }
    if (juntas) { await githubPutFile('juntas.json', juntas, msg, token); results.juntas = 'ok'; }
  } catch (err) {
    console.error(err);
    res.status(502).json({ error: err.message });
    return;
  }

  res.status(200).json({ ok: true, results });
};
