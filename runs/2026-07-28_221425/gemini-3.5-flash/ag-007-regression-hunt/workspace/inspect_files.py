import os

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            print(p)
            try:
                with open(p, 'r', encoding='utf-8') as fh:
                    print("---", p, "---")
                    print(fh.read())
            except Exception as e:
                print(e)
