import json

with open("output.json", encoding="utf-8") as fh:
    data = json.load(fh)

assert isinstance(data, list), "top level must be a list"
seen = set()
for rec in data:
    assert isinstance(rec, dict), rec
    assert set(rec) == {"email", "signup", "score"}, rec
    assert isinstance(rec["email"], str) and "@" in rec["email"]
    assert rec["email"] == rec["email"].lower(), rec
    assert isinstance(rec["signup"], str)
    y, m, d = rec["signup"].split("-")
    assert len(y) == 4 and len(m) == 2 and len(d) == 2, rec
    assert isinstance(rec["score"], int) and not isinstance(rec["score"], bool), rec
    seen.add(rec["email"])

assert len(seen) == len(data), "duplicate emails"
assert [r["email"] for r in data] == sorted(r["email"] for r in data), "not sorted"
print("OK:", len(data), "records, all checks passed")
