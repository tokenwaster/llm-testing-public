import csv
import json
from datetime import datetime

def clean_data():
    input_file = 'data.csv'
    output_file = 'output.json'
    
    rows = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email']
            signup = row['signup']
            score_str = row['score']
            
            # 1. Drop invalid rows
            if not email or '@' not in email or not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue # Or treat as empty/invalid

            # 2. Normalize emails to lowercase
            email = email.lower()
            
            # 3. Normalize dates
            # YYYY-MM-DD or DD/MM/YYYY
            if '-' in signup and len(signup) == 10:
                # Assume YYYY-MM-DD
                date_val = signup
            elif '/' in signup and len(signup) == 10:
                # Convert DD/MM/YYYY to YYYY-MM-DD
                try:
                    dt = datetime.strptime(signup, '%d/%m/%Y')
                    date_val = dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue # Invalid date format
            else:
                continue # Unexpected format

            rows.append({
                'email': email,
                'signup': date_val,
                'score': score
            })

    # 4. Deduplicate by email (keep highest score)
    unique_users = {}
    for row in rows:
        email = row['email']
        if email not in unique_users or row['score'] > unique_users[email]['score']:
            unique_users[email] = row
            
    final_list = list(unique_users.values())
    
    # 5. Sort by email ascending
    final_list.sort(key=lambda x: x['email'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2)

if __name__ == "__main__":
    clean_data()
