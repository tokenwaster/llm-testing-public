import csv, json, re
from datetime import datetime

def normalize_date(d):
    if re.match(r'\d{4}-\d{2}-\d{2}', d):
        return d
    # DD/MM/YYYY
    return datetime.strptime(d, '%d/%m/%Y').strftime('%Y-%m-%d')

rows=[]
with open('data.csv', newline='') as f:
    reader=csv.DictReader(f)
    for r in reader:
        email=r['email'].strip()
        signup=r['signup'].strip()
        score=r['score'].strip()
        if not email or '@' not in email or not score:
            continue
        email=email.lower()
        signup=normalize_date(signup)
        rows.append({'email':email,'signup':signup,'score':int(score)})
# dedupe keep highest score per email
best={}
for r in rows:
    e=r['email']
    if e not in best or r['score']>best[e]['score']:
        best[e]=r
out=sorted(best.values(), key=lambda x:x['email'])
with open('output.json','w') as f:
    json.dump(out,f,indent=2)
print('done',len(out))
