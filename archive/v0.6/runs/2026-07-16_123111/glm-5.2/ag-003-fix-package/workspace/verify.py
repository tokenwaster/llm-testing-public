from textstats.helpers import clean, tokenize

text = '"Dog." and \'dog\' are the same.'
tokens = tokenize(text)
cleaned = [clean(t) for t in tokens]
words = [c for c in cleaned if c]
print("tokens:", tokens)
print("cleaned:", cleaned)
print("words:", words)
print("lengths:", [len(w) for w in words])
print("sum:", sum(len(w) for w in words), "count:", len(words))
print("avg:", round(sum(len(w) for w in words) / len(words), 2))
