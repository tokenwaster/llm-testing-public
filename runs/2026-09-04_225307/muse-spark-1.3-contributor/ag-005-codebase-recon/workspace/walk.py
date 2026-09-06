import importlib
from pipeline import entry
cur = entry.START
chain = []
for i in range(7):
    mod = importlib.import_module(f"pipeline.{cur}")
    chain.append((cur, mod.SECRET_TOKEN, mod.NEXT))
    print(f"{i+1}: {cur} token={mod.SECRET_TOKEN} next={mod.NEXT}")
    cur = mod.NEXT
    if cur is None:
        break
# write 7th token
seventh_token = chain[6][1]
print("SEVENTH:", seventh_token)
open("answer.txt","w").write(seventh_token)
