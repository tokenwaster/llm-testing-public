from textstats import summarize

# Basic test
print(summarize("Hello world"))
# Case insensitivity
print(summarize("Dog. dog DOG"))
# Punctuation stripping
print(summarize("Hello, world!"))
# Whitespace handling (tabs, newlines, multiple)
print(summarize("a\tb\n  c   d"))
# Empty
print(summarize(""))
# Only punctuation tokens
print(summarize("!!! ... ??"))
# Mixed
print(summarize("  The quick brown fox.\nJumps! Over the; lazy dog.  "))
# Unique should be case-insensitive
print(summarize("Apple apple APPLE banana"))
# Average length
print(summarize("a bb ccc"))
