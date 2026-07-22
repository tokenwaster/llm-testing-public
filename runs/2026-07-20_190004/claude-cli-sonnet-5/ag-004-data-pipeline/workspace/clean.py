import csv
import json
import re

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row["email"].strip()
        signup = row["signup"].strip()
        score = row["score"].strip()

        if "@" not in email or not email or not score:
            continue

        email = email.lower()

        if re.match(r"^\d{4}-\d{2}-\d{2}$", signup):
            pass
        elif re.match(r"^\d{2}/\d{2}/\d{4}$", signup):
            d, m, y = signup.split("/")
            signup = f"{y}-{m}-{d}"
        else:
            continue

        rows.append({"email": email, "signup": signup, "score": int(score)})

best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
