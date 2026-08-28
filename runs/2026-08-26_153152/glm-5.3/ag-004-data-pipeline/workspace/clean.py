import csv
import json

rows = []
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for raw in reader:
        email = (raw.get("email") or "").strip()
        signup = (raw.get("signup") or "").strip()
        score = (raw.get("score") or "").strip()

        # 1. Drop invalid rows
        if not email or "@" not in email or not score:
            continue

        # 2. Normalize emails
        email = email.lower()

        # 3. Normalize dates
        if len(signup) == 10 and "/" in signup:
            dd, mm, yyyy = signup.split("/")
            signup = f"{yyyy}-{mm}-{dd}"

        # 4. Deduplicate by email, keep highest score
        rows.append({"email": email, "signup": signup, "score": int(score)})

best = {}
for r in rows:
    cur = best.get(r["email"])
    if cur is None or r["score"] > cur["score"]:
        best[r["email"]] = r

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
    f.write("\n")

print(json.dumps(result, indent=2))
