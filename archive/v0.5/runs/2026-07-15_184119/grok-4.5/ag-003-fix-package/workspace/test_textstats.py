from textstats import summarize

# Empty
print("empty:", summarize(""))
print("whitespace:", summarize("   \n\t  "))

# Basic
print("basic:", summarize("Hello world"))

# Multi whitespace
print("multi ws:", summarize("Hello   world\tfoo\nbar"))

# Punctuation and case
print("punct/case:", summarize('Dog. dog "DOG" hello!'))

# Only punctuation
print("only punct:", summarize("... !!! ???"))

# Mixed
print("mixed:", summarize("  The cat, the dog; the CAT.  "))
