#!/usr/bin/env python3
"""Converte o export do Primavera P6 (TSV) em cronograma.json.

Uso: python3 scripts/gerar_cronograma.py export_p6.tsv [cronograma.json]

Meta mensal acumulada (% 0-1) por etapa do painel, ponderada pelas horas
orçadas (Budgeted Nonlabor Units) e distribuída linearmente entre Start e
Finish de cada atividade STH-... - <etapa> - <material>.
"""
import csv, io, json, re, sys
from datetime import date, timedelta

# Etapa do P6 -> etapas do painel (Montagem de Tubulação alimenta Pré-Montagem e Soldado)
ETAPA_P6_PARA_PAINEL = {
    'Fabricação de Tubulação': ['Fabricado'],
    'Montagem de Tubulação': ['Pré-Montagem', 'Soldado'],
    'Testar, Lavar, Remontar': ['Teste Hidrostático'],
}
# Fora do mapeamento do painel; gravadas em 'extras' (Isolamento em m², Pintura sem unidade informada)
EXTRAS_P6 = {'Pintura': 'Pintura', 'Pintura de Fabricação': 'Pintura de Fabricação', 'Isolamento': 'Isolamento',
             'Montagem de Suporte': 'Montagem de Suporte', 'Montagem de Válvulas': 'Montagem de Válvulas'}
ABR = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
INICIO, FIM = date(2026, 10, 1), date(2027, 10, 31)  # fim geral da tubulação: 20/10/2027

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
    destinos = {e for v in ETAPA_P6_PARA_PAINEL.values() for e in v} | set(EXTRAS_P6.values())
    horas = {e: [0.0] * len(meses) for e in destinos}
    total = {e: 0.0 for e in horas}
    mat_h = {}  # (etapa painel, material) -> horas por mês
    for r in rows[1:]:
        if len(r) < len(h) - 5: continue
        a = dict(zip(h, r))
        m = re.match(r'STH-\S+ - (.+?) - A\w$', a['Activity Name'])
        if not m: continue
        etapas = ETAPA_P6_PARA_PAINEL.get(m[1]) or ([EXTRAS_P6[m[1]]] if m[1] in EXTRAS_P6 else None)
        if not etapas: continue
        mat = re.search(r' - (A\w)$', a['Activity Name'])[1]
        w, ini, fim = num(a['Budgeted Nonlabor Units']), dt(a['Start']), dt(a['Finish'])
        if w <= 0 or not ini or not fim: continue
        dias = max((fim - ini).days, 0) + 1
        for e in etapas:
            total[e] += w
            mh = mat_h.setdefault((e, mat), [0.0] * len(meses))
            for k in range(dias):
                dia = ini + timedelta(days=k)
                if (dia.year, dia.month) in meses:
                    i = meses.index((dia.year, dia.month))
                elif dia < INICIO:
                    i = 0  # já deveria estar feito ao iniciar
                else:
                    continue
                horas[e][i] += w / dias; mh[i] += w / dias
    def acumula(v, tot):
        acc, out = 0.0, []
        for x in v:
            acc += x; out.append(round(acc / tot, 4) if tot else 0)
        return out
    painel = {e for v in ETAPA_P6_PARA_PAINEL.values() for e in v}
    plano = {e: acumula(v, total[e]) for e, v in horas.items() if e in painel}
    extras = {e: acumula(v, total[e]) for e, v in horas.items() if e not in painel}
    # % acumulado por material, relativo ao total da etapa no mesmo material
    plano_material = {}
    for (e, mat), v in mat_h.items():
        if e in painel: plano_material.setdefault(e, {})[mat] = acumula(v, sum(v))
    json.dump({'fonte': 'Primavera P6 - disciplina TB', 'peso': 'horas orçadas (Budgeted Nonlabor Units)',
               'months': [f'{ABR[m-1]}/{str(y)[2:]}' for y, m in meses], 'plano': plano, 'plano_material': plano_material, 'extras': extras,
               'totais_p6': {e: round(t) for e, t in total.items()}},
              open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(dst, {e: plano[e][-1] for e in plano}, total)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'cronograma.json')
