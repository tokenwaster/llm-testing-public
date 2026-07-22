from textstats.helpers import tokenize, clean

s = '"Hello", \'world\' (foo) [bar]'
print("Input:", repr(s))
tokens = tokenize(s)
print("Tokens:", tokens)
cleaned = [clean(t) for t in tokens]
print("Cleaned:", cleaned)
words = [c for c in cleaned if c]
print("Words:", words)
print("Lengths:", [len(w) for w in words])
if words:
    print("Avg:", sum(len(w) for w in words)/len(words))
