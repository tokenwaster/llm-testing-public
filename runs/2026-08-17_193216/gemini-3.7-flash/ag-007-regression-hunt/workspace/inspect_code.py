import pytest
import sys

def inspect_file(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        print(f.read())

if __name__ == '__main__':
    inspect_file('toolkit/dates.py')
    inspect_file('toolkit/stats.py')
    inspect_file('toolkit/text.py')
