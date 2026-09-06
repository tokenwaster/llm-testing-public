from textstats import summarize

for text in ["Hello world hello", "", "...", "one", "aa bbb"]:
    r = summarize(text)
    types = {k: type(v).__name__ for k, v in r.items()}
    print(f"{text!r:24} -> {r}  {types}")
    assert set(r) == {"words", "unique", "avg_len"}, r
    assert isinstance(r["words"], int) and not isinstance(r["words"], bool)
    assert isinstance(r["unique"], int) and not isinstance(r["unique"], bool)
    assert isinstance(r["avg_len"], float)

# avg_len must be a float even when the mean is a whole number
assert summarize("aaa")["avg_len"] == 3.0
assert isinstance(summarize("aaa")["avg_len"], float)
print("\nAll type assertions passed.")
