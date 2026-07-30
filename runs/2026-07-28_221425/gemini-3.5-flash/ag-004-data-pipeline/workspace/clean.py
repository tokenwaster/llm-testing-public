import csv
import json
import re

def parse_date(date_str):
    # Match YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    # Match DD/MM/YYYY
    match = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"
    raise ValueError(f"Invalid date format: {date_str}")

def clean_data():
    records = []
    
    with open('data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            
            # Rule 1: Drop invalid rows
            if not email or '@' not in email or not score_str:
                continue
                
            # Rule 2: Normalize email to lowercase
            email_normalized = email.lower()
            
            # Rule 3: Normalize dates
            try:
                signup_normalized = parse_date(signup)
            except ValueError:
                # If date format doesn't match, maybe handle or skip? 
                # The rule states: "signup values are either YYYY-MM-DD (keep as is) or DD/MM/YYYY (convert)."
                # So we assume standard behavior or raise.
                continue
                
            score = int(score_str)
            
            records.append({
                'email': email_normalized,
                'signup': signup_normalized,
                'score': score
            })
            
    # Rule 4: Deduplicate by email keeping highest score
    # We can group records by normalized email, find the one with max score.
    by_email = {}
    for r in records:
        email = r['email']
        if email not in by_email:
            by_email[email] = r
        else:
            if r['score'] > by_email[email]['score']:
                by_email[email] = r
                
    # Rule 5: Sort remaining records by email ascending
    sorted_emails = sorted(by_email.keys())
    output_records = [by_email[email] for email in sorted_emails]
    
    # Write to output.json
    with open('output.json', 'w') as f:
        json.dump(output_records, f, indent=2)

if __name__ == '__main__':
    clean_data()
    print("Done")
