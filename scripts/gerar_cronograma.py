#!/usr/bin/env python3
"""Converte o export do Primavera P6 (TSV) em cronograma.json.

Uso: python3 scripts/gerar_cronograma.py export_p6.tsv [cronograma.json]

Meta mensal acumulada (% 0-1) por etapa do painel, ponderada pelas horas
orçadas (Budgeted Nonlabor Units) e distribuída linearmente entre Start e
Finish de cada atividade STH-... - <etapa> - <material>.
"""
import csv, io, json, re, sys
from datetime import date, timedelta

ETAPA_P6_PARA_PAINEL = {
    'Fabricação de Tubulação': 'Fabricado',
    'Montagem de Tubulação': 'Soldado',
    'Testar, Lavar, Remontar': 'Teste Hidrostático',
}
ABR = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
INICIO, FIM = date(2026, 10, 1), date(2027, 8, 31)

def num(s):
    s = re.sub(r'[^0-9,.\-]', '', s or '').replace('.', '').replace(',', '.')
    return float(s) if s else 0.0

def dt(s):
    m = re.match(r'(\d{2})/(\d{2})/(\d{4})', s or '')
    return date(int(m[3]), int(m[2]), int(m[1])) if m else None

def main(src, dst):
    txt = open(src, encoding='utf-8').read()
    txt = txt[txt.index('Activity ID'):]
    rows = list(csv.reader(io.StringIO(txt), delimiter='\t'))
    h = rows[0]
    meses = []
    d = INICIO
    while d <= FIM:
        meses.append((d.year, d.month)); d = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    horas = {e: [0.0] * len(meses) for e in set(ETAPA_P6_PARA_PAINEL.values())}
    total = {e: 0.0 for e in horas}
    for r in rows[1:]:
        if len(r) < len(h) - 5: continue
        a = dict(zip(h, r))
        m = re.match(r'STH-\S+ - (.+?) - A\w$', a['Activity Name'])
        if not m or m[1] not in ETAPA_P6_PARA_PAINEL: continue
        e = ETAPA_P6_PARA_PAINEL[m[1]]
        w, ini, fim = num(a['Budgeted Nonlabor Units']), dt(a['Start']), dt(a['Finish'])
        if w <= 0 or not ini or not fim: continue
        dias = max((fim - ini).days, 0) + 1
        total[e] += w
        for k in range(dias):
            dia = ini + timedelta(days=k)
            if (dia.year, dia.month) in meses:
                horas[e][meses.index((dia.year, dia.month))] += w / dias
            elif dia < INICIO:
                horas[e][0] += w / dias  # já deveria estar feito ao iniciar
    plano = {}
    for e, v in horas.items():
        acc, out = 0.0, []
        for x in v:
            acc += x; out.append(round(acc / total[e], 4) if total[e] else 0)
        plano[e] = out
    json.dump({'fonte': 'Primavera P6 - disciplina TB', 'peso': 'horas orçadas (Budgeted Nonlabor Units)',
               'months': [f'{ABR[m-1]}/{str(y)[2:]}' for y, m in meses], 'plano': plano},
              open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(dst, {e: plano[e][-1] for e in plano}, total)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'cronograma.json')
