import gzip
import json

f=gzip.open('data/mapdata/e2322d3cde06d.json.gz','rb')
j1=json.load(f)
f.close()
f=gzip.open('data/mapdata/584a7788950d0.json.gz','rb')
j2=json.load(f)
f.close()

json.dump(j1,open('j1.json','wb'),indent=2,sort_keys=True)
json.dump(j2,open('j2.json','wb'),indent=2,sort_keys=True)
