import csv, json, re
from datetime import datetime

def normalize_date(d):
    try:
        return d  # assume already YYYY-MM-DD
    except Exception:
        pass
    # if DD/MM/YYYY
    try:
        dt = datetime.strptime(d, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None

rows=[]
with open('data.csv',newline='') as f:
    reader=csv.DictReader(f)
    for r in reader:
        email=r['email'].strip()
        signup=r['signup'].strip()
        score=r['score'].strip()
        if not email or '@' not in email or not score:
            continue
        email=email.lower()
        # normalize date
        if re.match(r'^\d{4}-\d{2}-\d{2}$', signup):
            norm_date=signup
        else:
            try:
                dt=datetime.strptime(signup,'%d/%m/%Y')
                norm_date=dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        rows.append({'email':email,'signup':norm_date,'score':int(score)})
# deduplicate by email keep highest score
by_email={}
for r in rows:
    e=r['email']
    if e not in by_email or r['score']>by_email[e]['score']:
        by_email[e]=r
out=sorted(by_email.values(),key=lambda x:x['email'])
with open('output.json','w') as f:
    json.dump(out,f,indent=2)
print('written',len(out),'records')
