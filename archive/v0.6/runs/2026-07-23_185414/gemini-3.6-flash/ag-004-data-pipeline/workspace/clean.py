import csv
import json
from datetime import datetime

def clean_data(csv_path):
    valid_rows = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            
            # 1. Drop invalid rows: no @, email is empty, or score is empty
            if not email or '@' not in email or not score_str:
                continue
            
            score = int(score_str)
            
            # 2. Normalize emails to lowercase
            email_lower = email.lower()
            
            # 3. Normalize dates YYYY-MM-DD or DD/MM/YYYY
            if '/' in signup:
                dt = datetime.strptime(signup, '%d/%m/%Y')
                signup_norm = dt.strftime('%Y-%m-%d')
            else:
                signup_norm = signup
                
            valid_rows.append({
                'email': email_lower,
                'signup': signup_norm,
                'score': score
            })
            
    # 4. Deduplicate by email: keep highest score
    by_email = {}
    for item in valid_rows:
        em = item['email']
        if em not in by_email or item['score'] > by_email[em]['score']:
            by_email[em] = item
            
    # 5. Sort remaining records by email ascending
    sorted_records = sorted(by_email.values(), key=lambda x: x['email'])
    
    return sorted_records

if __name__ == '__main__':
    result = clean_data('data.csv')
    print("Cleaned result:")
    print(json.dumps(result, indent=2))
    
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
