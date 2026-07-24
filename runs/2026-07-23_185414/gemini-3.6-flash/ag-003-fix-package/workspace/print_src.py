import sys
sys.path.insert(0, '.')
import textstats.core
import textstats.helpers

with open('textstats/core.py') as f:
    print('core.py:')
    print(f.read())

with open('textstats/helpers.py') as f:
    print('helpers.py:')
    print(f.read())
