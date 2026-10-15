import pandas as pd, json, sys
O=sys.argv[1]
c=pd.read_csv(f'{O}/cand/votacao_candidato_munzona_2026_BR.csv',sep=';',encoding='latin1',usecols=['NR_TURNO','DS_CARGO','SG_UF','CD_MUNICIPIO','NR_ZONA','NR_CANDIDATO','QT_VOTOS_NOMINAIS_VALIDOS'])
c=c[(c.DS_CARGO=='Presidente')&(c.NR_TURNO==1)&(c.SG_UF!='ZZ')]
# maior adversário por município+zona
oth=c[c.NR_CANDIDATO!=13].groupby(['CD_MUNICIPIO','NR_ZONA','NR_CANDIDATO']).QT_VOTOS_NOMINAIS_VALIDOS.sum()
othz=oth.groupby(level=[0,1]).max()
othm=oth.groupby(level=[0,2]).sum().groupby(level=0).max()
xw=pd.read_csv(f'{O}/xw/municipios_brasileiros_tse.csv').set_index('codigo_ibge').codigo_tse
D=json.load(open(f'{O}/work/data.json'))
agg={'w':[0,0],'n':[0,0]}; nm=0; nz=0; tz=0
for ib,m in D['mun'].items():
    tse=int(xw[int(ib)])
    m['o']=int(othm.get(tse,0)); m['w']=1 if m['l']>m['o'] else 0
    nm+=m['w']
    for z in m['z']:
        o=int(othz.get((tse,z[0]),0)); z[5:]=[o]
    k='w' if m['w'] else 'n'; agg[k][0]+=m['a']; agg[k][1]+=m['b']
D['meta']['win']=agg
print('municipios lula venceu',nm,'de',len(D['mun']))
print({k:(v[0],round(v[1]/v[0]*100,2)) for k,v in agg.items()})
json.dump(D,open(f'{O}/work/data.json','w'),separators=(',',':'),ensure_ascii=False)
