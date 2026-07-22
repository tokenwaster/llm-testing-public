import importlib

entry = importlib.import_module('pipeline.entry')
current_name = entry.START

for _ in range(6):
    module = importlib.import_module(f'pipeline.{current_name}')
    current_name = module.NEXT

seventh_module = importlib.import_module(f'pipeline.{current_name}')
token = seventh_module.SECRET_TOKEN

with open('answer.txt', 'w') as f:
    f.write(token)