import csv
import json
from datetime import datetime

rows = []
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        signup = (row.get("signup") or "").strip()
        score = (row.get("score") or "").strip()
        if not email or "@" not in email or not score:
            continue
        email = email.lower()
        if "/" in signup:
            signup = datetime.strptime(signup, "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            # validate / keep YYYY-MM-DD
            signup = datetime.strptime(signup, "%Y-%m-%d").strftime("%Y-%m-%d")
        rows.append({"email": email, "signup": signup, "score": int(score)})

best = {}
for r in rows:
    prev = best.get(r["email"])
    if prev is None or r["score"] > prev["score"]:
        best[r["email"]] = r

out = [best[e] for e in sorted(best)]
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
    f.write("\n")

print(json.dumps(out, indent=2))
