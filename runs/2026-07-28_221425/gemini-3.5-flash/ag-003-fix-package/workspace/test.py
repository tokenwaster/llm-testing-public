import os

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            print("--- FILE:", path)
            with open(path, 'r', encoding='utf-8') as fh:
                print(fh.read())
            print("--- END OF FILE\n")
