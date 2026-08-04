from textstats import summarize

# Bug 1: tokenize only splits on " " single space, not any whitespace
r1 = summarize("hello   world")  # multiple spaces
print(f"Multiple spaces: {r1}")  # expected words=2, got?

r2 = summarize("hello\tworld")   # tab
print(f"Tab: {r2}")

r3 = summarize("hello\nworld")   # newline
print(f"Newline: {r3}")

# Bug 2: unique should be case-insensitive
r4 = summarize("Dog dog")
print(f"Case: {r4}")  # expected unique=1, got?

# Bug 3: punctuation stripping
r5 = summarize("Dog. dog!")
print(f"Punctuation: {r5}")  # expected unique=1

# Bug 4: token that is only punctuation should not count
r6 = summarize("hello ... world")
print(f"Only punctuation token: {r6}")  # expected words=2, unique=2

# Bug 5: empty input
r7 = summarize("")
print(f"Empty: {r7}")  # expected 0,0,0.0 -- might crash

# Bug 6: only punctuation
r8 = summarize("!!! ...")
print(f"Only punct: {r8}")  # expected 0,0,0.0