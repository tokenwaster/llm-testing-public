from textstats import summarize

print("Test 1 (basic):", summarize("Hello world hello"))
print("Test 2 (tabs/newlines):", summarize("hello\tworld\nhello"))
print("Test 3 (punctuation):", summarize("Dog. dog! 'cat'"))
print("Test 4 (punct-only token):", summarize("hello , world"))
print("Test 5 (empty):", summarize(""))
print("Test 6 (no words):", summarize("   \n\t  "))
