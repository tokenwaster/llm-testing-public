from textstats import summarize

print(summarize("Hello world"))
print(summarize("Hello\t\nworld"))
print(summarize("Dog. dog DOG"))
print(summarize("hello ... world"))
print(summarize(""))
print(summarize("   "))
