Your workspace contains a small Python package `textstats/` whose behaviour
does not match its specification. The bugs may be in any file. Do not change
any function names or signatures.

Specification for `textstats.summarize(text: str) -> dict`:

- Returns `{"words": int, "unique": int, "avg_len": float}`.
- `words` — total word count. Words are separated by **any** whitespace
  (spaces, tabs, newlines, multiple in a row).
- `unique` — number of distinct words, **case-insensitive**, ignoring leading
  and trailing punctuation (`.,;:!?"'()`): `"Dog."` and `"dog"` are the same
  word. A token that is *only* punctuation does not count as a word at all —
  neither in `words` nor `unique`.
- `avg_len` — mean length of the cleaned words (punctuation stripped),
  rounded to 2 decimals. For empty input (or input with no words) the result
  is `{"words": 0, "unique": 0, "avg_len": 0.0}` — it must not raise.

Explore the package, reproduce the failures with a quick script, fix the code
in place, and verify your fix by running it before you finish.
