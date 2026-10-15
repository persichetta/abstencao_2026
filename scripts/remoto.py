import json, glob, os, sys, unicodedata
O=sys.argv[1]
def norm(s): return unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().upper().strip()
D=json.load(open(f'{O}/work/data.json'))
mz={}; zr={}
for f in sorted(glob.glob(f'{O}/work/data/*.json')):
    uf=os.path.basename(f)[:2]
    for r in json.load(open(f)):
        a=sum(s[1] for s in r[6]); rl=r[9]
        mz.setdefault((uf,norm(r[3])),[0,0,0])[rl]+=a
        zr.setdefault(f'{uf}-{r[4]}',[0,0,0])[rl]+=a
for m in D['mun'].values(): m['ra']=mz.get((m['uf'],norm(m['n'])),[0,0,0])
D['meta']['zr']=zr
json.dump(D,open(f'{O}/work/data.json','w'),separators=(',',':'),ensure_ascii=False)
import statistics as st
ab=[m['b']/m['a'] for m in D['mun'].values()]; lu=[m['l']/m['v'] for m in D['mun'].values() if m['v']]
q=lambda x:[round(v,3) for v in st.quantiles(x,n=3)]
print('tercis abst',q(ab),'lula',q(lu))
sh=[(m['ra'][1]+m['ra'][2])/max(1,sum(m['ra'])) for m in D['mun'].values()]
print('mun com >=50% aptos em media/alta',sum(s>=.5 for s in sh),'20-50%',sum(.2<=s<.5 for s in sh))
