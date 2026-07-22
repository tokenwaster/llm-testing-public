import importlib

mod_name = "mod_27"
for i in range(7):
    m = importlib.import_module(f"pipeline.{mod_name}")
    token = m.SECRET_TOKEN
    nxt = m.NEXT
    print(f"{i+1}: {mod_name} token={token} next={nxt}")
    if i == 6:
        print("ANSWER:", token)
        with open("answer.txt", "w") as f:
            f.write(token)
    mod_name = nxt
