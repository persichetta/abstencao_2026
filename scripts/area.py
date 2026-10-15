import geopandas as gp, pandas as pd, json, glob, os, sys, unicodedata
S=sys.argv[1]
files={}
for p in glob.glob('/mnt/user-data/uploads/*_setores_CD2022*.gpkg')+glob.glob('/root/.claude/uploads/2d7b13fa-ee47-5677-aba9-6925c8fb2f0c/*_setores_CD2022.gpkg'):
    uf=os.path.basename(p).split('_setores')[0][-2:]; files.setdefault(uf,p)
xw=pd.read_csv(f'{S}/xw/municipios_brasileiros_tse.csv')
def norm(s): return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().upper().strip()
def cat(r):
    t,s=r.CD_TIPO,r.CD_SIT
    if t==1: return 1                       # favela e comunidade urbana
    if t in (5,9): return 7                 # indígena / quilombola
    if s in (5,6,7): return 5               # rural aglomerado
    if s==8: return 6                       # rural área dispersa
    if s in (1,2,3) and norm(r.NM_BAIRRO) in ('CENTRO','CENTRO HISTORICO','ZONA CENTRAL','CENTRO-SUL'): return 0
    if s==1: return 2
    if s==2: return 3
    if s==3: return 4
    return 8
stats={}
for uf in sorted(files):
    lv=json.load(open(f'{S}/work/data/{uf}.json'))
    pts=pd.DataFrame([(i,r[0],r[1]) for i,r in enumerate(lv)],columns=['i','lat','lon']).dropna()
    g=gp.GeoDataFrame(pts,geometry=gp.points_from_xy(pts.lon,pts.lat),crs='EPSG:4674')
    st=gp.read_file(files[uf],columns=['CD_SETOR','CD_SIT','CD_TIPO','NM_BAIRRO','CD_MUN'])
    st['CD_SIT']=pd.to_numeric(st.CD_SIT,errors='coerce'); st['CD_TIPO']=pd.to_numeric(st.CD_TIPO,errors='coerce')
    st['cat']=st.apply(cat,axis=1)
    j=gp.sjoin(g,st[['cat','CD_MUN','geometry']],how='left',predicate='within').drop_duplicates('i')
    miss=j.cat.isna()
    if miss.any():
        gm=g[g.i.isin(j[miss].i)].to_crs(5880); sm=st[['cat','CD_MUN','geometry']].to_crs(5880)
        n=gp.sjoin_nearest(gm,sm,how='left',max_distance=300).drop_duplicates('i').set_index('i')
        j=j.set_index('i'); j.loc[n.index,'cat']=n['cat']; j.loc[n.index,'CD_MUN']=n['CD_MUN']; j=j.reset_index()
    cmap=dict(zip(j.i,j.cat))
    for i,r in enumerate(lv):
        c=cmap.get(i); r.append(None if c is None or pd.isna(c) else int(c))
    json.dump(lv,open(f'{S}/work/data/{uf}.json','w'),separators=(',',':'),ensure_ascii=False)
    stats[uf]={'pts':len(pts),'sem_setor':int(j.cat.isna().sum()),'nearest':int(miss.sum())}
    print(uf,stats[uf],flush=True)
json.dump(stats,open(f'{S}/work/area_stats.json','w'))
