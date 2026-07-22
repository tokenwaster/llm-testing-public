import csv
import json
import re

with open("data.csv", newline="") as f:
    rows = list(csv.DictReader(f))

def normalize_date(s):
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", s)
    if m:
        d, mo, y = m.groups()
        return f"{y}-{mo}-{d}"
    raise ValueError(f"Unrecognized date format: {s}")

best = {}
for row in rows:
    email = row["email"].strip()
    score = row["score"].strip()
    if "@" not in email or not email or not score:
        continue
    email_norm = email.lower()
    signup = normalize_date(row["signup"].strip())
    score_int = int(score)
    if email_norm not in best or score_int > best[email_norm]["score"]:
        best[email_norm] = {"email": email_norm, "signup": signup, "score": score_int}

result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
