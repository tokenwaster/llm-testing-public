import csv
import json
import re

def clean_data():
    # Read the CSV file
    rows = []
    with open('data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # Step 1: Drop invalid rows (email contains no @, email is empty, or score is empty)
    valid_rows = []
    for row in rows:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score = row.get('score', '').strip()
        
        # Check if email is empty
        if not email:
            continue
        
        # Check if email contains @
        if '@' not in email:
            continue
        
        # Check if score is empty
        if not score:
            continue
        
        valid_rows.append({
            'email': email,
            'signup': signup,
            'score': int(score)
        })
    
    # Step 2: Normalize emails to lowercase
    for row in valid_rows:
        row['email'] = row['email'].lower()
    
    # Step 3: Normalize dates (convert DD/MM/YYYY to YYYY-MM-DD)
    def normalize_date(date_str):
        # Check if it's in DD/MM/YYYY format
        match = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', date_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month}-{day}"
        else:
            # Already in YYYY-MM-DD format
            return date_str
    
    for row in valid_rows:
        row['signup'] = normalize_date(row['signup'])
    
    # Step 4: Deduplicate by email (keep highest score)
    email_dict = {}
    for row in valid_rows:
        email = row['email']
        if email not in email_dict or row['score'] > email_dict[email]['score']:
            email_dict[email] = row
    
    deduped_rows = list(email_dict.values())
    
    # Step 5: Sort by email ascending
    sorted_rows = sorted(deduped_rows, key=lambda x: x['email'])
    
    # Format output (ensure score is int)
    output = []
    for row in sorted_rows:
        output.append({
            'email': row['email'],
            'signup': row['signup'],
            'score': int(row['score'])
        })
    
    return output

if __name__ == '__main__':
    result = clean_data()
    
    # Write to output.json
    with open('output.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Cleaned data written to output.json")
    print(json.dumps(result, indent=2))
