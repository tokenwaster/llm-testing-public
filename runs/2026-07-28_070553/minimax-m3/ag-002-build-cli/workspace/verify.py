import re
with open('sample.txt') as f:
    content = f.read()
print("Content repr:", repr(content))
print("Lines:", len(content.split('\n')) - (1 if content.endswith('\n') else 0))
print("Words:", re.findall(r'[a-z]+', content.lower()))