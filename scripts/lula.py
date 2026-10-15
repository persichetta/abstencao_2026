import pandas as pd, json, sys
O=sys.argv[1]
c=pd.read_csv(f'{O}/cand/votacao_candidato_munzona_2026_BR.csv',sep=';',encoding='latin1',usecols=['NR_TURNO','DS_CARGO','SG_UF','CD_MUNICIPIO','NR_ZONA','NR_CANDIDATO','QT_VOTOS_NOMINAIS_VALIDOS'])
c=c[(c.DS_CARGO=='Presidente')&(c.NR_TURNO==1)&(c.SG_UF!='ZZ')]
allv=c.groupby(['CD_MUNICIPIO','NR_ZONA']).QT_VOTOS_NOMINAIS_VALIDOS.sum()
lula=c[c.NR_CANDIDATO==13].groupby(['CD_MUNICIPIO','NR_ZONA']).QT_VOTOS_NOMINAIS_VALIDOS.sum()
d=pd.read_csv(f'{O}/tse/detalhe_votacao_munzona_2026_BRASIL.csv',sep=';',encoding='latin1')
d=d[(d.DS_CARGO=='Presidente')&(d.NR_TURNO==1)&(d.SG_UF!='ZZ')].set_index(['CD_MUNICIPIO','NR_ZONA'])
diff=(d.QT_TOTAL_VOTOS_VALIDOS-allv.reindex(d.index).fillna(0)).abs()
print('validos detalhe',d.QT_TOTAL_VOTOS_VALIDOS.sum(),'soma candidatos',allv.sum(),'linhas divergentes',(diff>0).sum())
xw=pd.read_csv(f'{O}/xw/municipios_brasileiros_tse.csv').set_index('codigo_ibge').codigo_tse
D=json.load(open(f'{O}/work/data.json'))
L=V=0; ufl={}
for ib,m in D['mun'].items():
    tse=int(xw[int(ib)]); ml=mv=0
    for z in m['z']:
        k=(tse,z[0]); l=int(lula.get(k,0)); v=int(d.QT_TOTAL_VOTOS_VALIDOS.get(k,0))
        z[3:]=[l,v]; ml+=l; mv+=v
    m['l']=ml; m['v']=mv; L+=ml; V+=mv
    u=ufl.setdefault(m['uf'],[0,0]); u[0]+=ml; u[1]+=mv
D['meta']['lula']=L; D['meta']['valid']=V; D['meta']['ufl']=ufl
print('lula',L,'validos',V,round(L/V*100,2))
r=pd.Series({k:m['l']/m['v'] for k,m in D['mun'].items() if m['v']})
print(r.quantile([0,.05,.25,.5,.75,.95,1]).round(3).tolist())
json.dump(D,open(f'{O}/work/data.json','w'),separators=(',',':'),ensure_ascii=False)
