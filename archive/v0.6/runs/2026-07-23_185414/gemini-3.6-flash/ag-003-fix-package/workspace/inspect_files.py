import os

for root, dirs, files in os.walk('.'):
    for f in files:
        p = os.path.join(root, f)
        print(p)
        print('---')
        with open(p, 'r', encoding='utf-8') as fh:
            print(fh.read())
        print('===')
