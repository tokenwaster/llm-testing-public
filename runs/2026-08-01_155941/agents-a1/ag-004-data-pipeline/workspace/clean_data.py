#!/usr/bin/env python3
import csv
import json
from datetime import datetime

def parse_date(date_str):
    """Convert date string. If it's DD/MM/YYYY, convert to YYYY-MM-DD."""
    if not date_str:
        return None
    # Try parsing as YYYY-MM-DD first
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return date_str  # Keep as is
    except ValueError:
        pass
    # Then try DD/MM/YYYY
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

def main():
    records = []
    
    with open('data.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            
            # Rule 1: Drop invalid rows (no @, empty email, or empty score)
            if '@' not in email:
                continue
            if not email:
                continue
            if not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue
            
            # Rule 2: Normalize emails to lowercase
            email_lower = email.lower()
            
            # Rule 3: Normalize dates
            signup_normalized = parse_date(signup)
            if not signup_normalized:
                continue
            
            records.append({
                'email': email_lower,
                'signup': signup_normalized,
                'score': score
            })
    
    # Rule 4: Deduplicate by email - keep row with highest score per email
    email_max = {}
    for rec in records:
        email = rec['email']
        if email not in email_max or rec['score'] > email_max[email]['score']:
            email_max[email] = rec
    
    # Get the deduplicated list and Rule 5: Sort by email ascending
    final_records = sorted(email_max.values(), key=lambda x: x['email'])
    
    # Write to output.json
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(final_records, f, indent=2)
    
    print(f"Written {len(final_records)} records to output.json")

if __name__ == '__main__':
    main()
