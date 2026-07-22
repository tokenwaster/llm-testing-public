#!/usr/bin/env python3
import os

# Directory containing pipeline modules
PIPELINE_DIR = "pipeline"

def get_module_attr(module_name, attr):
    """Read a module file and extract the value of an attribute."""
    path = os.path.join(PIPELINE_DIR, f"{module_name}.py")
    with open(path, 'r') as f:
        content = f.read()
    # Simple extraction: find "ATTR = value" or "ATTR='value'" or ATTR="value"
    import re
    match = re.search(rf'^\s*{attr}\s*=\s*(.+?)\s*$', content, re.MULTILINE)
    if match:
        value_str = match.group(1).strip()
        # Remove comments at end of line
        if '#' in value_str:
            value_str = value_str.split('#')[0].strip()
        # Handle string literals
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        # Handle None
        if value_str == 'None':
            return None
        return value_str
    return None

# Start from the START module
current = "mod_27"  # entry.py says START = "mod_27"

print(f"Starting at: {current}")

# We need to visit 7 modules total (including start)
for i in range(1, 8):
    token = get_module_attr(current, "SECRET_TOKEN")
    print(f"Module {i}: {current} -> SECRET_TOKEN={token}")
    
    if i == 7:
        # This is the 7th module - we have our answer
        break
    
    # Get NEXT to continue
    next_mod = get_module_attr(current, "NEXT")
    print(f"         -> NEXT={next_mod}")
    current = next_mod

print(f"\nAnswer (SECRET_TOKEN of 7th module): {token}")

# Write to answer.txt
with open("answer.txt", "w") as f:
    f.write(token)

print("Written to answer.txt")
