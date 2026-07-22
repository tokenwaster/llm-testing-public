import csv
import json
import re

rows = []
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        signup = (row.get("signup") or "").strip()
        score = (row.get("score") or "").strip()

        if "@" not in email or email == "" or score == "":
            continue

        email = email.lower()

        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", signup)
        if m:
            norm_signup = signup
        else:
            m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", signup)
            if m:
                day, month, year = m.groups()
                norm_signup = f"{year}-{month}-{day}"
            else:
                continue

        rows.append({"email": email, "signup": norm_signup, "score": int(score)})

best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
