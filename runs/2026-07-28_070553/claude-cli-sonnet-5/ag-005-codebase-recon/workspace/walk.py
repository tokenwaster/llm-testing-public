import importlib

entry = importlib.import_module('pipeline.entry')
name = entry.START
visited = []
for i in range(7):
    mod = importlib.import_module(f'pipeline.{name}')
    visited.append((name, mod.SECRET_TOKEN))
    name = mod.NEXT

for v in visited:
    print(v)
print('ANSWER:', visited[6][1])

with open('answer.txt', 'w') as f:
    f.write(visited[6][1])
