import importlib

cur = "mod_27"
for i in range(7):
    m = importlib.import_module(f"pipeline.{cur}")
    token = m.SECRET_TOKEN
    print(i + 1, cur, token, m.NEXT)
    if i == 6:
        answer = token
    nxt = m.NEXT
    cur = nxt

with open("answer.txt", "w") as f:
    f.write(answer)

print("ANSWER:", answer)
