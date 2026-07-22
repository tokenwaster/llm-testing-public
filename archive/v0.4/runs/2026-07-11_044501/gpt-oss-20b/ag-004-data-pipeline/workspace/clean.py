import csv, json, datetime

def normalize_date(d):
    try:
        return d  # assume already YYYY-MM-DD
    except Exception:
        pass
    # try DD/MM/YYYY
    try:
        dt=datetime.datetime.strptime(d,'%d/%m/%Y')
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
        try:
            dt=datetime.datetime.strptime(signup,'%Y-%m-%d')
            signup_norm=signup
        except ValueError:
            try:
                dt=datetime.datetime.strptime(signup,'%d/%m/%Y')
                signup_norm=dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        rows.append({'email':email,'signup':signup_norm,'score':int(score)})
# deduplicate by email keep highest score
by_email={}
for r in rows:
    e=r['email']
    if e not in by_email or r['score']>by_email[e]['score']:
        by_email[e]=r
out=sorted(by_email.values(),key=lambda x:x['email'])
with open('output.json','w') as f:
    json.dump(out,f,indent=2)
print('done',len(out))
