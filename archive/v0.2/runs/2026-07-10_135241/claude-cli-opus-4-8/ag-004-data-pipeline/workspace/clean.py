import csv, json

def norm_date(s):
    s = s.strip()
    if "/" in s:
        d, m, y = s.split("/")
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    return s

rows = []
with open("data.csv", newline="") as f:
    for r in csv.DictReader(f):
        email = (r["email"] or "").strip()
        score = (r["score"] or "").strip()
        if "@" not in email or email == "" or score == "":
            continue
        rows.append({
            "email": email.lower(),
            "signup": norm_date(r["signup"]),
            "score": int(score),
        })

# dedup by email, keep highest score
best = {}
for row in rows:
    e = row["email"]
    if e not in best or row["score"] > best[e]["score"]:
        best[e] = row

result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
