from textstats import summarize

print(summarize(''))
print(summarize('hello world'))
print(summarize('hello\t\nworld  foo'))
print(summarize('Dog. dog DOG, cat!'))
print(summarize('hello ... world'))
