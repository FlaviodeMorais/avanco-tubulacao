#!/usr/bin/env python3
"""gp_sop.json: grupo de prioridade (GP) de cada SOP, a partir do "Agrupamento por SOP_FIC_FVM.xlsx".

Uso: python3 scripts/gerar_gp_sop.py "Agrupamento por SOP_FIC_FVM.xlsx" [gp_sop.json]
O GP segue a rede de precedência (prioridade do CCM das malhas de linhas): GP01 antes de GP02 etc.
"""
import json, sys
import openpyxl

src, dst = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'gp_sop.json')
rows = list(openpyxl.load_workbook(src, read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True))
ix = {str(c).strip(): i for i, c in enumerate(rows[0]) if c}
gp = {}
for r in rows[1:]:
    sop, g = r[ix['SOP']], r[ix['GP']]
    if sop and g and str(g).startswith('GP') and str(sop).startswith('SOP-'):
        gp[str(sop).strip()] = str(g).strip()
json.dump({'fonte': 'Agrupamento por SOP_FIC_FVM.xlsx', 'gp': gp}, open(dst, 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
print(len(gp), 'SOP em', len(set(gp.values())), 'GP')
