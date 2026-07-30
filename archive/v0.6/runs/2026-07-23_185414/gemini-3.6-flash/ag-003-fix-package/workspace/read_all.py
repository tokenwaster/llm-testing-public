import glob

files = glob.glob('textstats/*.py')
for f in files:
    print('FILE:', f)
    with open(f, 'r') as fp:
        lines = fp.readlines()
        for i, line in enumerate(lines):
            print(f"{i+1}: {line.rstrip()}")
