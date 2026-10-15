import geopandas as gp, pandas as pd, numpy as np, json, glob, os, sys, unicodedata
from scipy.spatial import cKDTree
from pyproj import Transformer
O=sys.argv[1]
def norm(s): return unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper().strip()
files={}
for p in glob.glob('/mnt/user-data/uploads/*_setores_CD2022*.gpkg')+glob.glob('/root/.claude/uploads/2d7b13fa-ee47-5677-aba9-6925c8fb2f0c/*_setores_CD2022.gpkg'):
    files.setdefault(os.path.basename(p).split('_setores')[0][-2:],p)
xw=pd.read_csv(f'{O}/xw/municipios_brasileiros_tse.csv')
ibge={(r.uf,norm(r.nome_municipio)):int(r.codigo_ibge) for r in xw.itertuples()}
tr=Transformer.from_crs(4674,5880,always_xy=True)
allD=[]; munS={}; zoneS={}
os.makedirs(f'{O}/work/far',exist_ok=True)
for uf in sorted(files):
    lv=json.load(open(f'{O}/work/data/{uf}.json'))
    L=pd.DataFrame([(i,r[0],r[1],ibge.get((uf,norm(r[3]))),r[4]) for i,r in enumerate(lv)],columns=['i','lat','lon','mun','z']).dropna(subset=['lat','mun'])
    L['x'],L['y']=tr.transform(L.lon.values,L.lat.values)
    st=gp.read_file(files[uf],columns=['CD_SIT','CD_MUN'])
    st['CD_SIT']=pd.to_numeric(st.CD_SIT,errors='coerce'); st=st[st.CD_SIT!=9]
    st['CD_MUN']=pd.to_numeric(st.CD_MUN,errors='coerce').astype('Int64')
    rp=st.geometry.representative_point()
    pp=gp.GeoSeries(rp,crs=st.crs).to_crs(5880); ll=gp.GeoSeries(rp,crs=st.crs).to_crs(4674)
    st['x']=pp.x.values; st['y']=pp.y.values; st['lat']=ll.y.values; st['lon']=ll.x.values
    st['d']=np.nan; st['li']=-1
    for mun,g in st.groupby('CD_MUN'):
        Lm=L[L.mun==mun]
        if not len(Lm): continue
        d,k=cKDTree(Lm[['x','y']].values).query(g[['x','y']].values)
        st.loc[g.index,'d']=d/1000; st.loc[g.index,'li']=Lm.i.values[k]
    ok=st[st.li>=0]
    # catchment por local
    cs=ok.groupby('li').d.agg(['count','mean','max'])
    for i,r in enumerate(lv):
        c=cs.loc[i] if i in cs.index else None
        r[10:]=[[int(c['count']),round(float(c['mean']),1),round(float(c['max']),1)] if c is not None else None]
    json.dump(lv,open(f'{O}/work/data/{uf}.json','w'),separators=(',',':'),ensure_ascii=False)
    bins=np.digitize(ok.d.values,[2,5,10])
    for mun,b in zip(ok.CD_MUN.values,bins): munS.setdefault(int(mun),[0,0,0,0])[b]+=1
    for li,b in zip(ok.li.values,bins): zoneS.setdefault(f'{uf}-{lv[int(li)][4]}',[0,0,0,0])[b]+=1
    far=ok[ok.d>=2]
    json.dump([[round(a,4),round(o,4),round(float(dd),1)] for a,o,dd in zip(far.lat,far.lon,far.d)],open(f'{O}/work/far/{uf}.json','w'),separators=(',',':'))
    allD.append(ok.d.values)
    print(uf,len(st),'sem local',int((st.li<0).sum()),'>=2km',len(far),'>=10km',int((ok.d>=10).sum()),flush=True)
a=np.concatenate(allD); print('quantis setor->local km',np.round(np.quantile(a,[.5,.75,.9,.95,.99]),2))
D=json.load(open(f'{O}/work/data.json'))
for k,m in D['mun'].items(): m['sd']=munS.get(int(k),[0,0,0,0])
D['meta']['zs']=zoneS
json.dump(D,open(f'{O}/work/data.json','w'),separators=(',',':'),ensure_ascii=False)
