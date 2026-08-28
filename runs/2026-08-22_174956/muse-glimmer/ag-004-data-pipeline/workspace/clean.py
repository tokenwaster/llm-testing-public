import csv
import json
import re
from pathlib import Path

input_path = Path('data.csv')
output_path = Path('output.json')

date_pattern_ymd = re.compile(r'^\d{4}-\d{2}-\d{2}$')
date_pattern_dmy = re.compile(r'^(\d{2})/(\d{2})/(\d{4})$')

def normalize_date(s):
    s = s.strip()
    if date_pattern_ymd.match(s):
        return s
    m = date_pattern_dmy.match(s)
    if m:
        day, month, year = m.groups()
        return f"{year}-{month}-{day}"
    # fallback: return as is
    return s

records = {}
with input_path.open(newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email_raw = (row.get('email') or '').strip()
        signup_raw = (row.get('signup') or '').strip()
        score_raw = (row.get('score') or '').strip()

        # Rule 1: Drop invalid rows
        if not email_raw or '@' not in email_raw:
            continue
        if not score_raw:
            continue
        # score must be integer
        try:
            score = int(score_raw)
        except ValueError:
            continue

        email_norm = email_raw.lower()
        signup_norm = normalize_date(signup_raw)

        # Deduplicate: keep highest score
        if email_norm in records:
            if score > records[email_norm]['score']:
                records[email_norm] = {
                    'email': email_norm,
                    'signup': signup_norm,
                    'score': score
                }
        else:
            records[email_norm] = {
                'email': email_norm,
                'signup': signup_norm,
                'score': score
            }

# Sort by email ascending
sorted_records = sorted(records.values(), key=lambda x: x['email'])

# Ensure keys order? JSON objects unordered but we output dict with those keys.
output = [
    {'email': r['email'], 'signup': r['signup'], 'score': r['score']}
    for r in sorted_records
]

with output_path.open('w') as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
