import csv, json

rows = []
with open("data.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        email = (r["email"] or "").strip()
        signup = (r["signup"] or "").strip()
        score = (r["score"] or "").strip()

        # 1. Drop invalid rows
        if "@" not in email or email == "" or score == "":
            continue

        # 2. Normalize email
        email = email.lower()

        # 3. Normalize date
        if "/" in signup:
            d, m, y = signup.split("/")
            signup = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

        rows.append({"email": email, "signup": signup, "score": int(score)})

# 4. Deduplicate by email, keeping highest score
best = {}
for row in rows:
    if row["email"] not in best or row["score"] > best[row["email"]]["score"]:
        best[row["email"]] = row

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
