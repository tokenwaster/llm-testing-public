import csv
import json
import re

DATE_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_DMY = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")

def normalize_date(value: str) -> str:
    value = value.strip()
    if DATE_ISO.match(value):
        return value
    m = DATE_DMY.match(value)
    if m:
        dd, mm, yyyy = m.groups()
        return f"{yyyy}-{mm}-{dd}"
    raise ValueError(f"Unrecognized date format: {value!r}")

def main() -> None:
    with open("data.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        best = {}  # email -> record with highest score
        for row in reader:
            email = (row.get("email") or "").strip()
            score_raw = (row.get("score") or "").strip()
            signup = (row.get("signup") or "").strip()

            # Rule 1: drop invalid rows
            if not email or "@" not in email:
                continue
            if not score_raw:
                continue

            # Rule 2: normalize email
            email = email.lower()

            # Rule 3: normalize date
            signup = normalize_date(signup)

            score = int(score_raw)

            # Rule 4: dedupe by email, keep highest score (no ties)
            if email not in best or score > best[email]["score"]:
                best[email] = {"email": email, "signup": signup, "score": score}

    # Rule 5: sort by email ascending
    records = sorted(best.values(), key=lambda r: r["email"])

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
        f.write("\n")

if __name__ == "__main__":
    main()
