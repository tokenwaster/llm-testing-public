import csv,json,datetime

def normalize_date(d):
    try:
        # if already YYYY-MM-DD
        datetime.datetime.strptime(d,'%Y-%m-%d')
        return d
    except ValueError:
        pass
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
        score_str=r['score'].strip()
        if not email or '@' not in email or not score_str:
            continue
        email=email.lower()
        signup_norm=normalize_date(signup)
        if not signup_norm:
            continue
        try:
            score=int(score_str)
        except ValueError:
            continue
        rows.append({'email':email,'signup':signup_norm,'score':score})
# deduplicate keep highest score
best={}
for r in rows:
    e=r['email']
    if e not in best or r['score']>best[e]['score']:
        best[e]=r
records=sorted(best.values(),key=lambda x:x['email'])
with open('output.json','w') as f:
    json.dump(records,f,indent=2)
print('done',len(records))