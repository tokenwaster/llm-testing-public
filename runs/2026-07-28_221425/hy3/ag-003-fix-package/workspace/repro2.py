from textstats import summarize

# avg_len rounding check: lengths 1,2,3 -> 6/3 = 2.0 ; and 1,2 -> 1.5
print(summarize("a bb"))                       # words:2 unique:2 avg_len:1.5
print(summarize("(hello) world"))              # leading/trailing punct: words:2 unique:2 avg_len:5.5
print(summarize("A a A B b"))                  # words:5 unique:2
print(summarize("  tab\tand\nnewline  "))      # words:2 unique:2
