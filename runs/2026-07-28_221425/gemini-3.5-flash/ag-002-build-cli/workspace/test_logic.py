def count_lines_split(content):
    if not content:
        return 0
    lines_list = content.split('\n')
    if len(lines_list) > 1 and lines_list[-1] == '':
        lines_list.pop()
    return len(lines_list)

def count_lines_count(content):
    if not content:
        return 0
    if content.endswith('\n'):
        return content.count('\n')
    return content.count('\n') + 1

# Test combinations of newline, space, characters, empty
from itertools import product
chars = ['', 'a', '\n']
for p in product(chars, repeat=4):
    content = "".join(p)
    c1 = count_lines_split(content)
    c2 = count_lines_count(content)
    assert c1 == c2, f"Failed for {repr(content)}: split={c1}, count={c2}"

print("All logic combinations tested successfully!")
