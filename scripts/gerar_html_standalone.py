#!/usr/bin/env python3
"""Gera um HTML único (sem servidor, sem internet) a partir do painel.

Uso: python3 scripts/gerar_html_standalone.py LIBS_DIR [saida.html]
  LIBS_DIR com chart.js/dist/chart.umd.js, xlsx/dist/xlsx.full.min.js e jszip/dist/jszip.min.js
  (npm i chart.js@4.4.1 xlsx@0.18.5 jszip@3.10.1)

Embute as bibliotecas e os JSONs (data, juntas, cronograma, excluidos, ac_pequeno) no próprio
arquivo; o fetchJson do painel passa a ler primeiro dos dados embutidos.
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / 'ControlTub-Dashboard.V5.5.html'
JSONS = ['data.json', 'juntas.json', 'cronograma.json', 'excluidos.json', 'ac_pequeno.json', 'de_para_spool.json']


def main(libs, saida):
    libs = Path(libs)
    html = FONTE.read_text(encoding='utf-8')
    lib_js = {
        'Chart.js': libs / 'chart.js/dist/chart.umd.js',
        'xlsx': libs / 'xlsx/dist/xlsx.full.min.js',
        'jszip': libs / 'jszip/dist/jszip.min.js',
    }
    for chave, arq in lib_js.items():
        padrao = re.compile(r'<script src="https://cdnjs[^"]*' + re.escape(chave) + r'[^"]*"[^>]*></script>', re.I)
        codigo = arq.read_text(encoding='utf-8').replace('</script', '<\\/script')
        html, n = padrao.subn(lambda m: '<script>' + codigo + '</script>', html, count=1)
        assert n == 1, f'tag da biblioteca {chave} não encontrada'
    dados = {}
    for nome in JSONS:
        p = RAIZ / nome
        if p.exists():
            dados[nome] = json.loads(p.read_text(encoding='utf-8'))
    emb = json.dumps(dados, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    marcador = '<script>\n'
    i = html.index(marcador, html.index('</head>')) if '</head>' in html else html.index(marcador)
    html = html[:i] + '<script>window.__EMBUTIDO__=' + emb + ';</script>\n' + html[i:]
    antigo = "async function fetchJson(url){\n  const res"
    assert antigo in html
    html = html.replace(antigo, "async function fetchJson(url){\n  if(window.__EMBUTIDO__ && window.__EMBUTIDO__[url]) return window.__EMBUTIDO__[url];\n  const res")
    html = html.replace('V5.5', 'V5.6')
    Path(saida).write_text(html, encoding='utf-8')
    print(saida, round(len(html) / 1e6, 2), 'MB')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else str(RAIZ / 'ControlTub-Dashboard.V5.6.html'))
