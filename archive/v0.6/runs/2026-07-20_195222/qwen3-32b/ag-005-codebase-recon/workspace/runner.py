import re

def get_var_value(content, var_name):
    escaped_var = re.escape(var_name)
    # Match assignment with either single or double quotes
    pattern_str = rf"{escaped_var}\s*=\s*(?:'([^']*)'|"([^"]*)")"
    pattern = re.compile(pattern_str)
    match = pattern.search(content)
    return match.group(1) or match.group(2) if match else None

# Load entry module to get START
with open('entry.py') as f:
    content = f.read()
next_module = get_var_value(content, 'START')
tokens = []

for _ in range(6):  # Start is first, need 6 more hops (total 7)
    with open(f'pipeline/{next_module}.py') as f:
        content = f.read()
    next_module = get_var_value(content, 'NEXT')
    tokens.append(get_var_value(content, 'SECRET_TOKEN'))

# Write final token to answer.txt
with open('answer.txt', 'w') as f:
    f.write(tokens[-1])