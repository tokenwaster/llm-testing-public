import textstats, importlib
importlib.reload(textstats)
print(textstats.summarize('Dog. dog!'))
print(textstats.summarize('  !  '))