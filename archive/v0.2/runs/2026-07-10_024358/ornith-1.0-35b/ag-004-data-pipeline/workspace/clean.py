import csv, json, re
from datetime import datetime

rows = []
with open("data.csv", newline="") as f:
    for r in csv.DictReader(f):
        email = (r.get("email") or "").strip()
        signup = (r.get("signup") or "").strip()
        score_str = (r.get("score") or "").strip()

        # Step 1: drop invalid
        if not email or "@" not in email or not score_str:
            continue

        # Step 2: normalize email
        email = email.lower()

        # Step 3: normalize date
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", signup)
        if m:
            date_str = signup
        else:
            dt = datetime.strptime(signup, "%d/%m/%Y")
            date_str = dt.strftime("%Y-%m-%d")

        score = int(score_str)
        rows.append({"email": email, "signup": date_str, "score": score})

# Step 4: deduplicate by email, keep highest score
best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

# Step 5: sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
