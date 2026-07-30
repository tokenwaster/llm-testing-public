import re

def title_case_v1(s: str) -> str:
    # Just capitalize first letter of each space-separated word, lowercasing the rest?
    return " ".join(w[0].upper() + w[1:].lower() if w else "" for w in s.split(" "))

print("V1 'it's a dog's life':", title_case_v1("it's a dog's life"))
print("V1 'o'neill's':", title_case_v1("o'neill's"))
print("V1 'hello world':", title_case_v1("hello world"))
print("V1 'HELLO':", title_case_v1("HELLO"))
print("V1 '':", title_case_v1(""))
