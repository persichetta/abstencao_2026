import pandas as pd, json, glob, os, sys, math, unicodedata
O=sys.argv[1]
def norm(s): return unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper().strip()
s=pd.read_csv(f'{O}/work/secao_lula.csv')
xw=pd.read_csv(f'{O}/xw/municipios_brasileiros_tse.csv')
sede=pd.read_csv(f'{O}/xw/municipios.csv')[['codigo_ibge','latitude','longitude']]
xw=xw.merge(sede,on='codigo_ibge',how='left')
s=s.merge(xw[['codigo_tse','nome_municipio']],left_on='CD_MUNICIPIO',right_on='codigo_tse',how='left')
s['key']=s.SG_UF+'|'+s.nome_municipio.map(norm)+'|'+s.NR_ZONA.astype(str)+'|'+s.NR_SECAO.astype(str)
SL=dict(zip(s.key,zip(s.l,s.v)))
seat={(r.uf,norm(r.nome_municipio)):(r.latitude,r.longitude) for r in xw.itertuples()}
munE={}  # (uf, NORMNAME) -> [e0,e1,e2]
def hav(a,b,c,d):
    R=6371;p=math.radians
    x=math.sin(p(c-a)/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2
    return 2*R*math.asin(math.sqrt(x))
def rem(cat,dist):
    if cat in (6,7): return 2
    dense = cat in (0,1,2)
    if not dense and dist is not None and dist>=25: return 2
    if cat in (3,4,5): return 1
    if not dense and dist is not None and dist>=8: return 1
    return 0
miss=tot=0; cnt=[0,0,0]
for f in sorted(glob.glob(f'{O}/work/data/*.json')):
    uf=os.path.basename(f)[:2]; lv=json.load(open(f))
    for r in lv:
        lat,lon,nome,mun,z,bairro,secs,cat=r[:8]
        sd=seat.get((uf,norm(mun)))
        dist=round(hav(lat,lon,sd[0],sd[1]),1) if lat is not None and sd and not pd.isna(sd[0]) else None
        e=0.0
        for sec in secs:
            tot+=1; lv_=SL.get(f'{uf}|{norm(mun)}|{z}|{sec[0]}')
            if lv_ is None: miss+=1; l=v=0
            else: l,v=map(int,lv_)
            sec[3:]=[l,v]
            if v: e+=sec[2]*l/v
        rl=rem(cat,dist); cnt[rl]+=1
        r[8:]=[dist,rl]
        me=munE.setdefault((uf,norm(mun)),[0.0,0.0,0.0]); me[rl]+=e
    json.dump(lv,open(f,'w'),separators=(',',':'),ensure_ascii=False)
print('secoes sem voto por candidato',miss,'de',tot,'| locais por nivel baixa/media/alta',cnt)
D=json.load(open(f'{O}/work/data.json'))
nomatch=0
for m in D['mun'].values():
    e=munE.get((m['uf'],norm(m['n'])))
    if e is None: nomatch+=1; e=[0,0,0]
    m['e']=[round(x) for x in e]
print('municipios sem match',nomatch)
E=[sum(m['e'][i] for m in D['mun'].values()) for i in range(3)]
D['meta']['E']=E; print('eleitores do lula estimados entre abstentes por nivel',E)
json.dump(D,open(f'{O}/work/data.json','w'),separators=(',',':'),ensure_ascii=False)
