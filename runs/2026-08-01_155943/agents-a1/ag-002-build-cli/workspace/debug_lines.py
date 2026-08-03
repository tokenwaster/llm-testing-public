with open('newline_test.txt', 'r') as f:
    content = f.read()
print(repr(content))
print(f"len(splitlines): {len(content.splitlines())}")
