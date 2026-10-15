import pandas as pd, json, sys, os, glob
S=sys.argv[1]; out=f'{S}/work/site/data'; os.makedirs(out,exist_ok=True)
UFS=sorted(os.path.basename(p)[-6:-4] for p in glob.glob(f'{S}/secao/detalhe_votacao_secao_2026_??.csv'))
UFS=[u for u in UFS if u not in('BR','ZZ')]
tot={'sec':0,'semcoord':0,'aptos':0,'abst':0,'locais':0}
summary={}
BR=pd.read_csv(f'{S}/secao/detalhe_votacao_secao_2026_BR.csv',sep=';',encoding='latin1',
        usecols=['SG_UF','NR_TURNO','CD_MUNICIPIO','NM_MUNICIPIO','NR_ZONA','NR_SECAO','DS_CARGO','QT_APTOS','QT_ABSTENCOES','NR_LOCAL_VOTACAO','NM_LOCAL_VOTACAO','ST_SECAO_INSTALADA'])
print(BR.DS_CARGO.value_counts())
BR=BR[(BR.DS_CARGO=='Presidente')&(BR.NR_TURNO==1)]
for uf in UFS:
    s=BR[BR.SG_UF==uf]
    l=pd.read_csv(f'{S}/locais/eleitorado_local_votacao_2026_{uf}.csv',sep=';',encoding='latin1',
        usecols=['NR_TURNO','CD_MUNICIPIO','NR_ZONA','NR_SECAO','NR_LATITUDE','NR_LONGITUDE','NM_BAIRRO'],dtype={'CD_MUNICIPIO':int})
    l=l[l.NR_TURNO==1].drop(columns='NR_TURNO').drop_duplicates(['CD_MUNICIPIO','NR_ZONA','NR_SECAO'])
    for c in('NR_LATITUDE','NR_LONGITUDE'): l[c]=pd.to_numeric(l[c].astype(str).str.replace(',','.'),errors='coerce')
    m=s.merge(l,on=['CD_MUNICIPIO','NR_ZONA','NR_SECAO'],how='left')
    bad=m.NR_LATITUDE.isna()|(m.NR_LATITUDE==-1)|(m.NR_LATITUDE==0)|(m.NR_LATITUDE>6)|(m.NR_LATITUDE<-34)|(m.NR_LONGITUDE>-28)|(m.NR_LONGITUDE<-74)
    tot['sec']+=len(m); tot['semcoord']+=int(bad.sum()); tot['aptos']+=int(m.QT_APTOS.sum()); tot['abst']+=int(m.QT_ABSTENCOES.sum())
    # agrupar por local de votação
    locs=[]
    for (mun,nm,z,lv),g in m.groupby(['CD_MUNICIPIO','NM_MUNICIPIO','NR_ZONA','NR_LOCAL_VOTACAO']):
        gg=g[~bad.loc[g.index]]
        lat=round(float(gg.NR_LATITUDE.median()),5) if len(gg) else None
        lon=round(float(gg.NR_LONGITUDE.median()),5) if len(gg) else None
        secs=[[int(r.NR_SECAO),int(r.QT_APTOS),int(r.QT_ABSTENCOES)] for r in g.sort_values('NR_SECAO').itertuples()]
        locs.append([lat,lon,str(g.NM_LOCAL_VOTACAO.iloc[0]).title(),nm.title(),int(z),str(g.NM_BAIRRO.dropna().iloc[0]).title() if g.NM_BAIRRO.notna().any() else '',secs])
    tot['locais']+=len(locs)
    json.dump(locs,open(f'{out}/{uf}.json','w'),separators=(',',':'),ensure_ascii=False)
    summary[uf]=len(locs)
    print(uf,len(m),int(bad.sum()),len(locs),os.path.getsize(f'{out}/{uf}.json')//1024,'KB',flush=True)
print(tot)
json.dump(tot,open(f'{S}/work/secao_tot.json','w'))
