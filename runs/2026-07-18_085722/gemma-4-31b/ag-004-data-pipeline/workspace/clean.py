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
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            
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
            # signup values are either YYYY-MM-DD or DD/MM/YYYY
            if '/' in signup:
                try:
                    dt = datetime.strptime(signup, '%d/%m/%Y')
                    signup = dt.strftime('%Y-%m-%d')
                except ValueError:
                    # If date is invalid, we might need to decide what to do. 
                    # The prompt doesn't explicitly say how to handle malformed dates, 
                    # but usually they should be handled or dropped.
                    pass
            elif '-' in signup:
                # Check if it matches YYYY-MM-DD format roughly
                try:
                    datetime.strptime(signup, '%Y-%m-%d')
                except ValueError:
                    pass
            
            rows.append({
                'email': email,
                'signup': signup,
                'score': score
            })

    # 4. Deduplicate by email (keep highest score)
    unique_users = {}
    for row in rows:
        email = row['email']
        if email not in unique_users or row['score'] > unique_users[email]['score']:
            unique_users[email] = row
            
    # 5. Sort by email ascending
    sorted_users = sorted(unique_users.values(), key=lambda x: x['email'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_users, f, indent=2)

if __name__ == "__main__":
    clean_data()
