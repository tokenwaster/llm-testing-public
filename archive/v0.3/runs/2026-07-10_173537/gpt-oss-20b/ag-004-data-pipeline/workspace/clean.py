import csv,json
from datetime import datetime

def normalize_date(d):
    try:
        dt=datetime.strptime(d,'%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    try:
        dt=datetime.strptime(d,'%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None

rows=[]
with open('data.csv',newline='') as f:
    reader=csv.DictReader(f)
    for r in reader:
        email=r['email'].strip()
        if not email or '@' not in email:
            continue
        signup=r['signup'].strip()
        score_str=r['score'].strip()
        if not score_str:
            continue
        try:
            score=int(score_str)
        except ValueError:
            continue
        email=email.lower()
        signup_norm=normalize_date(signup)
        if not signup_norm:
            continue
        rows.append({'email':email,'signup':signup_norm,'score':score})
by_email={}
for r in rows:
    e=r['email']
    if e not in by_email or r['score']>by_email[e]['score']:
        by_email[e]=r
out=sorted(by_email.values(), key=lambda x:x['email'])
with open('output.json','w') as f:
    json.dump(out,f,indent=2)
print('done',len(out))
