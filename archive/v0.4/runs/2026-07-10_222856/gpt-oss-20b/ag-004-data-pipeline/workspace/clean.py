import csv, json, re
from datetime import datetime

def normalize_date(d):
    if re.match(r'\d{4}-\d{2}-\d{2}', d):
        return d
    # DD/MM/YYYY
    try:
        dt = datetime.strptime(d, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None

rows=[]
with open('data.csv', newline='') as f:
    reader=csv.DictReader(f)
    for row in reader:
        email=row['email'].strip()
        signup=row['signup'].strip()
        score=row['score'].strip()
        # drop invalid
        if not email or '@' not in email or not score:
            continue
        email=email.lower()
        date=normalize_date(signup)
        if not date:
            continue
        rows.append({'email':email,'signup':date,'score':int(score)})
# deduplicate by email keep highest score
by_email={}
for r in rows:
    e=r['email']
    if e not in by_email or r['score']>by_email[e]['score']:
        by_email[e]=r
out=sorted(by_email.values(), key=lambda x:x['email'])
with open('output.json','w') as f:
    json.dump(out,f,indent=2)
print('done',len(out))
