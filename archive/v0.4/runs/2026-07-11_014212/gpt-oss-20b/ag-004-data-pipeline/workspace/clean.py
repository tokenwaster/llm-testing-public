import csv, json, datetime

def normalize_date(d):
    try:
        return d  # assume YYYY-MM-DD
    except Exception:
        pass
    if '/' in d:
        day, month, year = d.split('/')
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return d

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
        try:
            if '/' in signup:
                day, month, year = signup.split('/')
                signup=f"{year}-{int(month):02d}-{int(day):02d}"
        except Exception:
            pass
        rows.append({'email':email,'signup':signup,'score':int(score)})
# deduplicate by email keep highest score
best={}
for r in rows:
    e=r['email']
    if e not in best or r['score']>best[e]['score']:
        best[e]=r
out=sorted(best.values(), key=lambda x:x['email'])
with open('output.json','w') as f:
    json.dump(out,f,indent=2)
print('done',len(out))