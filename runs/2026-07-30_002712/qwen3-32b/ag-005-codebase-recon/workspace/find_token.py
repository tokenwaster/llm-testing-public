import importlib

# Read START value from pipeline/entry.py
with open('pipeline/entry.py', 'r') as f:
    start_line = None
    for line in f:
        if line.startswith('START'):
            start_line = line.strip()
            break
if not start_line:
    raise Exception('START not found')
start_value = start_line.split('=')[1].strip().strip("'").strip('\"')

current_module = start_value
count = 1

while count <7:
    module = importlib.import_module(f'pipeline.{current_module}')
    current_module = module.NEXT
    count +=1

final_module = importlib.import_module(f'pipeline.{current_module}')
print(final_module.SECRET_TOKEN)