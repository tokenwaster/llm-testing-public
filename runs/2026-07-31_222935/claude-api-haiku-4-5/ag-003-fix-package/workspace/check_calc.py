from textstats import summarize

# Test 6: "Hello ... world"
text = "Hello ... world"
print("Test: 'Hello ... world'")
words_list = ["Hello", "world"]  # dots are punctuation only, so ignored
print(f"  Words: {words_list}")
print(f"  Lengths: {[len(w) for w in words_list]}")
print(f"  Average: ({5} + {5}) / 2 = {10/2}")
result = summarize(text)
print(f"  Result: {result}")
print()

# Test 10: "'Hello!' (world)"
text = "'Hello!' (world)"
print("Test: \"'Hello!' (world)\"")
words_list = ["Hello", "world"]
print(f"  Words: {words_list}")
print(f"  Lengths: {[len(w) for w in words_list]}")
print(f"  Average: ({5} + {5}) / 2 = {10/2}")
result = summarize(text)
print(f"  Result: {result}")
