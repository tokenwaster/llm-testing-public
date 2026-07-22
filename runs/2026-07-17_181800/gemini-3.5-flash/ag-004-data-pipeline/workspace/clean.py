import csv
import json
import re

def clean_data():
    input_file = 'data.csv'
    output_file = 'output.json'
    
    valid_rows = []
    
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            
            # Rule 1: Drop invalid rows
            if not email or '@' not in email:
                continue
            if not score_str:
                continue
                
            try:
                score = int(score_str)
            except ValueError:
                # If score is not an integer, we can treat it as invalid or empty
                continue
                
            # Rule 2: Normalize emails to lowercase
            email_normalized = email.lower()
            
            # Rule 3: Normalize dates
            # signup values are either YYYY-MM-DD or DD/MM/YYYY
            if re.match(r'^\d{4}-\d{2}-\d{2}$', signup):
                signup_normalized = signup
            elif re.match(r'^\d{2}/\d{2}/\d{4}$', signup):
                day, month, year = signup.split('/')
                signup_normalized = f"{year}-{month}-{day}"
            else:
                # If date format doesn't match, we can skip or handle it
                continue
                
            valid_rows.append({
                'email': email_normalized,
                'signup': signup_normalized,
                'score': score
            })
            
    # Rule 4: Deduplicate by email (keep highest score)
    best_records = {}
    for row in valid_rows:
        email = row['email']
        if email not in best_records or row['score'] > best_records[email]['score']:
            best_records[email] = row
            
    # Rule 5: Sort by email, ascending
    sorted_records = sorted(best_records.values(), key=lambda x: x['email'])
    
    # Write to output.json
    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_records, f, indent=2)
        
    print("Cleaned records:")
    print(json.dumps(sorted_records, indent=2))

if __name__ == '__main__':
    clean_data()
