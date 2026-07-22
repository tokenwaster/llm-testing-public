import csv, json

rows = []
with open("data.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        email = (r["email"] or "").strip()
        score = (r["score"] or "").strip()
        if not email or "@" not in email or not score:
            continue
        email = email.lower()
        signup = r["signup"].strip()
        if "/" in signup:
            d, m, y = signup.split("/")
            signup = f"{y}-{m}-{d}"
        rows.append({"email": email, "signup": signup, "score": int(score)})

best = {}
for r in rows:
    if r["email"] not in best or r["score"] > best[r["email"]]["score"]:
        best[r["email"]] = r

out = sorted(best.values(), key=lambda r: r["email"])
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
