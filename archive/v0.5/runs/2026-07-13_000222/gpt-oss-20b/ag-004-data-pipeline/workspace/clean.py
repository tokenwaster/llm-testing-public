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
        if not email or '@' not in email:
            continue
        score=r['score'].strip()
        if not score:
            continue
        signup=r['signup'].strip()
        # normalize
        email=email.lower()
        try:
            datetime.datetime.strptime(signup, '%Y-%m-%d')
            norm_date=signup
        except ValueError:
            day,month,year=signup.split('/')
            norm_date=f"{year}-{int(month):02d}-{int(day):02d}"
        rows.append({'email':email,'signup':norm_date,'score':int(score)})
# deduplicate
by_email={}
for r in rows:
    e=r['email']
    if e not in by_email or r['score']>by_email[e]['score']:
        by_email[e]=r
out=sorted(by_email.values(), key=lambda x:x['email'])
with open('output.json','w') as f:
    json.dump(out,f,indent=2)
print('done',len(out))