Create a command-line tool `wordstats.py` in your workspace.

Usage: `python wordstats.py <path-to-text-file>`

It must print exactly three lines to stdout:

```
lines: <number of lines in the file>
words: <total word count>
top: <word> <count>
```

Definitions:
- A *word* is a maximal run of ASCII letters (`a`–`z`) after lowercasing the
  whole text. Digits, punctuation and underscores separate words.
- `lines` is the number of lines in the file (as split by newline; a trailing
  final newline does not add an extra line).
- `top` is the most frequent word and its count. Ties are broken alphabetically
  (earliest wins). If the file has no words, print `top: - 0`.

Create the file, then test it yourself against a sample file before finishing.
