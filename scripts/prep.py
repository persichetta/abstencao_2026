import pandas as pd, json, sys
S=sys.argv[1]
d=pd.read_csv(f'{S}/tse/detalhe_votacao_munzona_2026_BRASIL.csv',sep=';',encoding='latin1',dtype={'CD_MUNICIPIO':int})
p=d[(d.DS_CARGO=='Presidente')&(d.NR_TURNO==1)&(d.SG_UF!='ZZ')]
xw=pd.read_csv(f'{S}/xw/municipios_brasileiros_tse.csv')
p=p.merge(xw[['codigo_tse','codigo_ibge']],left_on='CD_MUNICIPIO',right_on='codigo_tse',how='left')
miss=p[p.codigo_ibge.isna()][['SG_UF','NM_MUNICIPIO']].drop_duplicates()
print('sem ibge:',miss.values.tolist())
geo=json.load(open(f'{S}/geo/mun.json'))
gids={f['properties']['id'] for f in geo['features']}
out={}
for (ib,uf,nm),g in p.groupby(['codigo_ibge','SG_UF','NM_MUNICIPIO']):
    ap=int(g.QT_APTOS.sum()); ab=int(g.QT_ABSTENCOES.sum())
    z=[[int(r.NR_ZONA),int(r.QT_APTOS),int(r.QT_ABSTENCOES)] for r in g.sort_values('NR_ZONA').itertuples()]
    out[str(int(ib))]={'n':nm.title(),'uf':uf,'a':ap,'b':ab,'z':z}
nogeo=[(k,v['n'],v['uf'],v['a']) for k,v in out.items() if k not in gids]
print('sem geometria:',nogeo)
print('geo sem dado:',len(gids-set(out)))
# uf totals
uf=p.groupby('SG_UF')[['QT_APTOS','QT_ABSTENCOES']].sum()
ufd={k:[int(r.QT_APTOS),int(r.QT_ABSTENCOES)] for k,r in uf.iterrows()}
zon=p.groupby(['SG_UF','NR_ZONA'])[['QT_APTOS','QT_ABSTENCOES']].sum()
zr=(zon.QT_ABSTENCOES/zon.QT_APTOS)
print('zonas',len(zr),'min',zr.min(),'max',zr.max(), zr.idxmax(), zr.idxmin())
r=pd.Series({k:v['b']/v['a'] for k,v in out.items()}); print(r.describe()); print(r.quantile([.05,.25,.5,.75,.95]))
meta={'gen':str(d.DT_GERACAO.iloc[0]),'aptos':int(p.QT_APTOS.sum()),'abst':int(p.QT_ABSTENCOES.sum()),'zonas':int(len(zr)),'uf':ufd}
json.dump({'meta':meta,'mun':out},open(f'{S}/work/data.json','w'),separators=(',',':'),ensure_ascii=False)
