import csv
import json
from datetime import datetime

def clean_data(input_csv_path, output_json_path):
    records = []
    
    with open(input_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            score_str = row.get('score', '').strip()
            signup = row.get('signup', '').strip()
            
            # Rule 1: Drop invalid rows (no @, empty email, empty score)
            if not email or '@' not in email:
                continue
            if not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue
                
            # Rule 2: Normalize emails to lowercase
            email = email.lower()
            
            # Rule 3: Normalize dates (YYYY-MM-DD or DD/MM/YYYY to YYYY-MM-DD)
            if '/' in signup:
                # DD/MM/YYYY
                dt = datetime.strptime(signup, '%d/%m/%Y')
                signup_norm = dt.strftime('%Y-%m-%d')
            else:
                # YYYY-MM-DD (or parse to verify)
                dt = datetime.strptime(signup, '%Y-%m-%d')
                signup_norm = dt.strftime('%Y-%m-%d')
                
            records.append({
                'email': email,
                'signup': signup_norm,
                'score': score
            })
            
    # Rule 4: Deduplicate by email (keep highest score)
    best_records = {}
    for r in records:
        email = r['email']
        if email not in best_records or r['score'] > best_records[email]['score']:
            best_records[email] = r
            
    # Rule 5: Sort remaining records by email ascending
    sorted_records = sorted(best_records.values(), key=lambda x: x['email'])
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_records, f, indent=2)

if __name__ == '__main__':
    clean_data('data.csv', 'output.json')
    print("Done")
