#!/usr/bin/env python3
"""Gera cronograma.json cruzando o peso do CTB com o cronograma do Primavera P6.

Uso:
  python3 scripts/gerar_cronograma.py EXPORT_P6.tsv ControlTub_Planilha_Formulas.xlsx de_para_sth.tsv [cronograma.json]

Entradas
  EXPORT_P6.tsv   export do P6 (TSV) com atividades 'STH-... - <etapa> - <material>'
  planilha CTB    aba Dados_Spools (peso, material, linha, datas por etapa)
  de_para_sth.tsv LINHA | STH TOYO (CTB) | STH HC2 (P6)

Método
  1. Cada spool do CTB é ligado ao STH do P6 pela LINHA (de_para_sth.tsv).
  2. Para cada etapa do painel, o peso ainda NÃO realizado (spool sem data da etapa)
     é somado por STH × material (AC/AI/AL).
  3. Esse peso é distribuído dia a dia entre início e término da atividade do P6
     correspondente (mesmo STH e material) e acumulado por mês.
  4. Saída: % acumulado do peso restante por etapa. O painel aplica
     meta = Base + (escopo − Base) × %.
"""
import csv, io, json, re, sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

import openpyxl

# etapa do painel -> (atividade do P6, coluna em Dados_Spools)
ETAPAS = {
    'Fabricado':          ('Fabricação de Tubulação', 12),
    'Pré-Montagem':       ('Montagem de Tubulação', 14),
    'Soldado':            ('Montagem de Tubulação', 16),
    'Teste Hidrostático': ('Testar, Lavar, Remontar', 19),
}
ABR = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
INICIO, FIM = date(2026, 10, 1), date(2027, 10, 31)  # fim geral da tubulação: 20/10/2027


def norm(s):
    return re.sub(r'\s+', '', s or '').upper()


def chave_base(s):
    """'24"-GC-4710-00934-Bb-NI+A1:A2' -> '24"|GC|4710|00934' (ignora sufixo de revisão)."""
    p = norm(s).split('-')
    return '|'.join(p[:4]) if len(p) >= 4 else norm(s)


def dt(s):
    m = re.match(r'(\d{2})/(\d{2})/(\d{4})', s or '')
    return date(int(m[3]), int(m[2]), int(m[1])) if m else None


def excluir(linha, status_fab, status_mon, sth):
    """Motivo de exclusão do escopo: linhas da 6100 e tudo que estiver cancelado."""
    if '-6100-' in (linha or ''):
        return 'linha 6100'
    txt = ' '.join(str(x or '') for x in (linha, status_fab, status_mon, sth))
    if 'CANCELAD' in txt.upper():
        return 'cancelado'
    return None


def ac_pequeno(r):
    """Linhas em AC com diâmetro até 2\": avanço de fabricação/montagem zerado (FAB - Não iniciado)."""
    return r[5] == 'AC' and isinstance(r[23], (int, float)) and r[23] <= 2


# etapa do painel -> coluna em Dados_Spools (datas de fabricação e montagem)
COL_ETAPA = {'Fabricado': 12, 'Programado': 13, 'Pré-Montagem': 14, 'Visual de Ajuste': 15,
             'Soldado': 16, 'Visual de Solda': 17, 'Liberado END': 18, 'Teste Hidrostático': 19}
MES_IDX = {a: i for i, a in enumerate(['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'])}


def gera_ac_pequeno(spools, excluidos_keys, dst, data_json='data.json'):
    """ac_pequeno.json: ajustes sobre a Base publicada (data.json).

    - AC <= 2": avanço de fabricação/montagem zerado (spool segue no escopo, FAB - Não iniciado)
    - linhas 6100 e cancelados: saem do escopo (peso, nº de STH/SOP/linhas) e do avanço
    Datas lidas da planilha CTB (aproximado até novo upload ON-SITE).
    """
    d = json.load(open(data_json, encoding='utf-8'))
    unid = {(a[0], a[1]): a[3] for a in d['records']}
    ends = []
    for m in d['months']:
        y, mo = 2000 + int(m[4:]), MES_IDX[m[:3]]
        ends.append(datetime(y + (mo == 11), (mo + 1) % 12 + 1, 1) - timedelta(seconds=1))
    n = len(ends)
    vazio = lambda: defaultdict(lambda: [0.0] * n)
    baixa_u = defaultdict(vazio)      # unidade -> etapa -> toneladas a tirar por mês
    baixa_s = defaultdict(vazio)      # SOP -> etapa -> idem
    chaves, ton_ac = [], 0.0
    sop = defaultdict(lambda: {'linhas': set(), 'sths': set(), 'spools': 0, 'excl_ton': 0.0,
                               'baixa_fab': 0.0, 'baixa_lib': 0.0})
    sths, sops = set(), set()
    for r in spools:
        k = f'{r[0]}|{r[1]}'
        peso = float(r[4] or 0)
        fora = k in excluidos_keys or bool(excluir(r[2], r[8], r[9], None))
        pequeno = ac_pequeno(r) and not fora
        so = r[6] or '?'
        reg = sop[so]
        if fora:
            reg['excl_ton'] += peso
        else:
            reg['linhas'].add(r[2]); reg['spools'] += 1
            if r[7]:
                reg['sths'].add(r[7]); sths.add(r[7])
            sops.add(so)
        if pequeno:
            chaves.append(k); ton_ac += peso
        if fora or pequeno:               # avanço sai da Base
            for etapa, col in COL_ETAPA.items():
                dt_ = r[col]
                if isinstance(dt_, datetime):
                    for i, fim in enumerate(ends):
                        if dt_ <= fim:
                            baixa_u[unid.get((r[0], r[1]), '?')][etapa][i] += peso
                            baixa_s[so][etapa][i] += peso
            if isinstance(r[COL_ETAPA['Fabricado']], datetime):
                reg['baixa_fab'] += peso
            if isinstance(r[COL_ETAPA['Liberado END']], datetime):
                reg['baixa_lib'] += peso
    arred = lambda bx: {u: {e: [round(x, 3) for x in v] for e, v in et.items()} for u, et in bx.items()}
    out = {
        'regra': 'AC <= 2" zerado (FAB - Nao iniciado); linhas 6100 e cancelados fora do escopo',
        'aproximado': 'datas lidas da planilha CTB (pode divergir do ON-SITE ate novo upload)',
        'months': d['months'], 'ton': round(ton_ac, 3), 'spools': chaves,
        'baixa_ton': arred(baixa_u), 'baixa_sop': arred(baixa_s),
        'sth_total_n': len(sths), 'sop_total_n': len(sops),
        'sop': {k: {'linhas': len(v['linhas']), 'sths': len(v['sths']), 'spools': v['spools'],
                    'excl_ton': round(v['excl_ton'], 3),
                    'baixa_fab': round(v['baixa_fab'], 3), 'baixa_lib': round(v['baixa_lib'], 3)}
                for k, v in sop.items()},
    }
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    return len(chaves), ton_ac


def le_depara(path):
    por_linha = defaultdict(list)
    for l in open(path, encoding='utf-8').read().split('\n')[1:]:
        c = l.split('\t')
        if len(c) >= 3 and c[0].strip():
            por_linha[c[0].strip()].append(c[2].strip())
    exato = {norm(k): Counter(v).most_common(1)[0][0] for k, v in por_linha.items()}
    base = {}
    for k, v in exato.items():
        base.setdefault(chave_base(k), v)
    return exato, base


def le_p6(path):
    txt = open(path, encoding='utf-8').read()
    txt = txt[txt.index('Activity ID'):]
    rows = list(csv.reader(io.StringIO(txt), delimiter='\t'))
    h = rows[0]
    atv = {}  # (sth, atividade, material) -> (inicio, fim)
    for r in rows[1:]:
        if len(r) < len(h) - 5:
            continue
        a = dict(zip(h, r))
        m = re.match(r'(STH-\S+) - (.+?) - (A\w)$', a['Activity Name'])
        ini, fim = dt(a['Start']), dt(a['Finish'])
        if m and ini and fim:
            atv[(m[1], m[2], m[3])] = (ini, fim)
    return atv


def le_spools(path):
    wb = openpyxl.load_workbook(path, read_only=True)
    out = []
    for r in wb['Dados_Spools'].iter_rows(min_row=2, values_only=True):
        if not r[0]:
            continue
        out.append(r)
    return out


def main(p6, xlsx, depara, dst):
    atv = le_p6(p6)
    exato, base = le_depara(depara)
    spools = le_spools(xlsx)
    meses = []
    d = INICIO
    while d <= FIM:
        meses.append((d.year, d.month)); d = (d.replace(day=28) + timedelta(days=4)).replace(day=1)

    horas = {e: [0.0] * len(meses) for e in ETAPAS}   # peso (ton) por mês
    resto = Counter(); casado = Counter(); sem_sth = Counter(); sem_atv = Counter()
    sem_sth_linhas = Counter(); sem_atv_sth = Counter()
    excluido = Counter(); total_ton = 0.0; spools_cancelados = set()
    for r in spools:
        linha, peso, mat = r[2], float(r[4] or 0), r[5]
        sth = exato.get(norm(linha)) or base.get(chave_base(linha))
        total_ton += peso
        motivo = excluir(linha, r[8], r[9], sth)
        if motivo:                       # fora do escopo: não entra em nenhuma etapa
            if motivo == 'cancelado':
                spools_cancelados.add(f'{r[0]}|{r[1]}')
            excluido[motivo] += peso
            continue
        for etapa, (nome_p6, col) in ETAPAS.items():
            if r[col] and not ac_pequeno(r):   # etapa já realizada -> Base (AC <= 2" volta ao zero)
                continue
            resto[etapa] += peso
            if not sth or not sth.startswith('STH-'):
                sem_sth[etapa] += peso; sem_sth_linhas[(linha, sth)] += peso; continue
            janela = atv.get((sth, nome_p6, mat)) or next(
                (v for (s, n, m), v in atv.items() if s == sth and n == nome_p6), None)
            if not janela:
                sem_atv[etapa] += peso; sem_atv_sth[(sth, mat)] += peso; continue
            casado[etapa] += peso
            ini, fim = janela
            dias = max((fim - ini).days, 0) + 1
            for k in range(dias):
                dia = ini + timedelta(days=k)
                if (dia.year, dia.month) in meses:
                    i = meses.index((dia.year, dia.month))
                elif dia < INICIO:
                    i = 0
                else:
                    continue
                horas[etapa][i] += peso / dias

    json.dump({'regra': 'excluir linhas com -6100- e itens cancelados', 'spools_cancelados': sorted(spools_cancelados)},
              open('excluidos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    n_ac, t_ac = gera_ac_pequeno(spools, set(spools_cancelados), 'ac_pequeno.json')
    print('AC <= 2" zerados:', n_ac, 'spools', round(t_ac, 1), 'ton')
    plano, plano_ton = {}, {}
    for e, v in horas.items():
        tot = sum(v); acc = 0.0; pct = []; ton = []
        for x in v:
            acc += x
            pct.append(round(acc / tot, 4) if tot else 0); ton.append(round(acc, 3))
        plano[e] = pct; plano_ton[e] = ton

    json.dump({
        'fonte': 'Primavera P6 (disciplina TB) × peso do CTB, ligados pela linha (de_para_sth.tsv)',
        'peso': 'peso restante do CTB (ton) distribuído entre início e término da atividade do STH',
        'months': [f'{ABR[m-1]}/{str(y)[2:]}' for y, m in meses],
        'plano': plano, 'plano_ton': plano_ton,
        'conferencia': {
            'restante_ton': {e: round(v, 1) for e, v in resto.items()},
            'casado_ton': {e: round(v, 1) for e, v in casado.items()},
            'sem_sth_ton': {e: round(v, 1) for e, v in sem_sth.items()},
            'sem_atividade_p6_ton': {e: round(v, 1) for e, v in sem_atv.items()},
            'excluido_ton': {k: round(v, 1) for k, v in excluido.items()},
            'escopo_ctb_ton': round(total_ton, 1),
            'escopo_sem_excluidos_ton': round(total_ton - sum(excluido.values()), 1),
        },
    }, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

    print('Excluído (ton):', {k: round(v, 1) for k, v in excluido.items()}, '| escopo', round(total_ton, 1), '->', round(total_ton - sum(excluido.values()), 1))
    print('Restante (ton):', {e: round(v, 1) for e, v in resto.items()})
    print('Casado com P6 :', {e: round(v, 1) for e, v in casado.items()})
    print('Sem STH       :', {e: round(v, 1) for e, v in sem_sth.items()})
    print('Sem atividade :', {e: round(v, 1) for e, v in sem_atv.items()})
    print('Linhas sem STH (top):', sem_sth_linhas.most_common(8))
    print('STH x mat sem atividade (top):', sem_atv_sth.most_common(8))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'cronograma.json')
