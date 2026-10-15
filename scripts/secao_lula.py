import pandas as pd, sys, numpy as np
O=sys.argv[1]
d=pd.read_csv(f'{O}/vsec/votacao_secao_2026_BR.csv',sep=';',encoding='latin1',usecols=['NR_TURNO','SG_UF','CD_MUNICIPIO','NR_ZONA','NR_SECAO','NR_VOTAVEL','QT_VOTOS'],dtype={'NR_TURNO':'int8','SG_UF':'category','CD_MUNICIPIO':'int32','NR_ZONA':'int16','NR_SECAO':'int16','NR_VOTAVEL':'int16','QT_VOTOS':'int32'})
print(d.NR_TURNO.value_counts()); d=d[d.NR_TURNO==1]

k=['SG_UF','CD_MUNICIPIO','NR_ZONA','NR_SECAO']
val=d[~d.NR_VOTAVEL.isin([95,96,97])]
l=val[val.NR_VOTAVEL==13].groupby(k,observed=True).QT_VOTOS.sum().rename('l')
v=val.groupby(k,observed=True).QT_VOTOS.sum().rename('v')
o=val[val.NR_VOTAVEL!=13].groupby(k,observed=True).QT_VOTOS.max().rename('o')  # maior adversário na seção
s=pd.concat([l,v,o],axis=1).fillna(0).astype(int).reset_index()
print(len(s), s.l.sum(), s.v.sum())
s.to_csv(f'{O}/work/secao_lula.csv',index=False)
