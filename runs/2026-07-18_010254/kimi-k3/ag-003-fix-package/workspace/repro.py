"""Quick checks for textstats.summarize against the spec."""
from textstats import summarize

def check(name, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'} {name}: got={got} want={want}")
    return ok

results = []

# Basic whitespace handling (tabs, newlines, multiple spaces)
results.append(check(
    "whitespace",
    summarize("hello  world\tfoo\nbar"),
    {"words": 4, "unique": 4, "avg_len": 4.0},
))

# Case-insensitive uniqueness + punctuation stripping
results.append(check(
    "case/punct",
    summarize("Dog. dog DOG!"),
    {"words": 3, "unique": 1, "avg_len": 3.0},
))

# Punctuation-only tokens don't count
results.append(check(
    "punct-only",
    summarize("Hello, world... !!!"),
    {"words": 2, "unique": 2, "avg_len": 5.0},
))

# Empty input must not raise
try:
    results.append(check("empty", summarize(""), {"words": 0, "unique": 0, "avg_len": 0.0}))
except Exception as e:
    print(f"FAIL empty: raised {type(e).__name__}: {e}")
    results.append(False)

# Whitespace-only input
try:
    results.append(check("spaces-only", summarize("   \t\n  "), {"words": 0, "unique": 0, "avg_len": 0.0}))
except Exception as e:
    print(f"FAIL spaces-only: raised {type(e).__name__}: {e}")
    results.append(False)

# avg_len rounding
results.append(check(
    "rounding",
    summarize("aa bb c"),
    {"words": 3, "unique": 3, "avg_len": 1.67},
))

# Return type sanity: ints, float
r = summarize("one two")
results.append(check(
    "types",
    (type(r["words"]), type(r["unique"]), type(r["avg_len"])),
    (int, int, float),
))

print("\nALL PASS" if all(results) else "\nSOME FAILURES")
