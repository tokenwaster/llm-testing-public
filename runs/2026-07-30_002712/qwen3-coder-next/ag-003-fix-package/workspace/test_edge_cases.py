from textstats import summarize

# Edge case: only spaces
result = summarize("   ")
print(f"Only spaces: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}

# Edge case: newlines and tabs mixed
result = summarize("\n\n\t\n\t\t\n")
print(f"Only whitespace chars: {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}

# Edge case: words with punctuation only on edges
result = summarize('"""Hello""", \'world\' (foo) [bar]')
print(f"Punctuation at edges: {result}")

# Edge case: punctuation inside word should stay
result = summarize("can't won't it's")
print(f"Apostrophes in middle: {result}")

# Edge case: single word with punctuation
result = summarize("Hello!")
print(f"Single word with punctuation: {result}")
assert result == {"words": 1, "unique": 1, "avg_len": 5.0}

# Edge case: single empty string after cleaning (punctuation only)
result = summarize(".")
print(f"Only punctuation '.': {result}")
assert result == {"words": 0, "unique": 0, "avg_len": 0.0}

# Edge case: mixed words and punctuation
result = summarize("Hello, world! How are you?")
print(f"Mixed sentence: {result}")

print("\nAll edge case tests passed!")
