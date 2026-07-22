import csv, json, re
from datetime import datetime

def normalize_date(d):
    if re.match(r'\d{4}-\d{2}-\d{2}', d):
        return d
    # DD/MM/YYYY
    try:
        dt=datetime.strptime(d,'%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return None

def main():
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
            date=normalize_date(signup)
            if not date:
                continue
            score=int(score_str)
            rows.append({'email':email,'signup':date,'score':score})
    # dedupe by email keep highest score
    best={}
    for r in rows:
        e=r['email']
        if e not in best or r['score']>best[e]['score']:
            best[e]=r
    out=sorted(best.values(), key=lambda x:x['email'])
    with open('output.json','w') as f:
        json.dump(out,f,indent=2)
if __name__=='__main__':
    main()
