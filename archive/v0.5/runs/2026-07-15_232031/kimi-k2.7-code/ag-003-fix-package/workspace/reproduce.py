from textstats import summarize

print(summarize("Dog. dog"))  # expect {'words': 2, 'unique': 1, 'avg_len': 3.0}
print(summarize("a\tb"))  # expect {'words': 2, 'unique': 2, 'avg_len': 1.0}
print(summarize("..."))  # expect {'words': 0, 'unique': 0, 'avg_len': 0.0}
print(summarize(""))  # expect {'words': 0, 'unique': 0, 'avg_len': 0.0}
