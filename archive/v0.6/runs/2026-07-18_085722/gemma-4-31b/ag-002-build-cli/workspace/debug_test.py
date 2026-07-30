import re
text = "line1\nline2\n"
print(f"Lines: {len(text.splitlines())}")
print(f"Words: {re.findall(r'[a-z]+', text.lower())}")
