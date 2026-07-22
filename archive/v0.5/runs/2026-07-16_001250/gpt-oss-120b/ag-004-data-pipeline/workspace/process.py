import csv
import json
import sys
from datetime import datetime

def parse_date(date_str):
    # If format contains '/', assume DD/MM/YYYY
    if '/' in date_str:
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return date_str  # fallback, though shouldn't happen
    else:
        # Assume already YYYY-MM-DD
        return date_str

def main():
    input_path = 'data.csv'
    output_path = 'output.json'
    rows = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()
            # Rule 1: drop invalid rows
            if not email or '@' not in email or not score_str:
                continue
            # Normalize email
            email = email.lower()
            # Normalize date
            signup = parse_date(signup)
            # Convert score to int
            try:
                score = int(score_str)
            except ValueError:
                continue
            rows.append({
                'email': email,
                'signup': signup,
                'score': score,
            })
    # Deduplicate by email, keep highest score
    best_by_email = {}
    for r in rows:
        email = r['email']
        if email not in best_by_email or r['score'] > best_by_email[email]['score']:
            best_by_email[email] = r
    # Sort by email
    result = [best_by_email[email] for email in sorted(best_by_email)]
    # Write JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
