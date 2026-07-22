from textstats.helpers import tokenize, clean

text = 'hello  world\ttest\nfoo'
tokens = tokenize(text)
print(f'Tokens from split(" "): {tokens}')
print(f'Number of tokens: {len(tokens)}')
print()

# What should happen with split()
tokens_correct = text.split()
print(f'Tokens from split() (no args): {tokens_correct}')
print(f'Number of tokens: {len(tokens_correct)}')
