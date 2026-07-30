#!/usr/bin/env python3
"""Run wordstats.py against a battery of test cases."""

import os
import subprocess
import sys

SCRIPT = 'wordstats.py'

# Recall the spec:
#   word = maximal run of ASCII letters (a-z) after lowering
#   lines = split by newline; trailing final newline does NOT add a line
#   top: most frequent; ties broken alphabetically (earliest wins)
#   if no words:  top: - 0

CASES = [
    # (filename, contents, expected lines, expected words, expected top line)

    # --- empty / word-free ---
    ('empty.txt',           '',                                                    'lines: 0',   'words: 0',  'top: - 0'),
    ('just_nl.txt',         '\n',                                                  'lines: 1',   'words: 0',  'top: - 0'),
    ('no_words.txt',        '!!! 123 4567 _ _ __ ??\n',                            'lines: 1',   'words: 0',  'top: - 0'),
    ('unicode_only.txt',    'café déjà vu\n',
                            # After lowering, only ASCII letters are kept.
    # 'café'  -> 'caf' (é breaks)
    # 'déjà'  -> 'd' then 'j' (é and à break), so 'd' and 'j' are separate runs
    # 'vu'    -> 'vu'
    # Total: 4 words, all tied at 1, alpha tie-break picks 'caf'.
                            'lines: 1', 'words: 4', 'top: caf 1'),

    # --- single word / mixed case ---
    ('single.txt',          'Hello\n',                                             'lines: 1',   'words: 1',  'top: hello 1'),
    ('mixed_case.txt',      'Hello HELLO hello HeLLo\n',                           'lines: 1',   'words: 4',  'top: hello 4'),
    ('mixed_case2.txt',     'Foo foo FOO fOo\n',                                   'lines: 1',   'words: 4',  'top: foo 4'),

    # --- trailing newline handling ---
    ('no_trailing_nl.txt',  'a b a',                                               'lines: 1',   'words: 3',  'top: a 2'),
    ('trailing_nl.txt',     'a b a\n',                                             'lines: 1',   'words: 3',  'top: a 2'),

    # --- tie-breaking ---
    ('tie.txt',             'apple banana apple Banana\n',                         'lines: 1',   'words: 4',  'top: apple 2'),
    ('tie_alpha.txt',       'banana banana apple apple\n',                         'lines: 1',   'words: 4',  'top: apple 2'),
    ('threeway_tie.txt',    'zebra yak yak zebra apple apple\n',                   'lines: 1',   'words: 6',  'top: apple 2'),

    # --- punctuation / apostrophe / digits / underscore as separators ---
    ('apostrophe.txt',      "don't stop,stop. stop\n",
        # Maximal ASCII-letter runs: 'don', 't', 'stop', 'stop', 'stop'
                            'lines: 1', 'words: 5', 'top: stop 3'),
    ('digits_split.txt',    'abc-123-def xyz999\n',
        # 'abc-123-def' -> 'abc','def'
        # 'xyz999'      -> 'xyz' ('9's are not letters)
                            'lines: 1', 'words: 3', 'top: abc 1'),
    ('underscore.txt',      'snake_case_case snake snake\n',
                            'lines: 1', 'words: 5', 'top: snake 3'),

    # --- multi-line ---
    ('multiline.txt',       'a\nb\na\n',                                           'lines: 3',   'words: 3',  'top: a 2'),
    ('multiline_tie.txt',   'hello hello\nworld world\n',                          'lines: 2',   'words: 4',  'top: hello 2'),

    # --- top is a tie with alpha break across lines ---
    ('alpha_tie.txt',       'banana apple\napple banana\n',                        'lines: 2',   'words: 4',  'top: apple 2'),
]

failures = 0
for name, contents, exp_lines, exp_words, exp_top in CASES:
    with open(name, 'w', encoding='utf-8') as f:
        f.write(contents)
    result = subprocess.run(
        [sys.executable, SCRIPT, name],
        capture_output=True, text=True,
    )
    actual = [ln for ln in result.stdout.split('\n') if ln != '']
    ok = (result.returncode == 0
          and len(actual) == 3
          and actual[0] == exp_lines
          and actual[1] == exp_words
          and actual[2] == exp_top)
    status = 'PASS' if ok else 'FAIL'
    if not ok:
        failures += 1
    print(f'{status}  {name}')
    if not ok:
        print(f'    expected: {exp_lines} | {exp_words} | {exp_top}')
        print(f'    actual:   {actual}')
        if result.stderr:
            print(f'    stderr:   {result.stderr!r}')
    os.remove(name)

print()
print(f'{len(CASES) - failures}/{len(CASES)} cases passed')
sys.exit(1 if failures else 0)
