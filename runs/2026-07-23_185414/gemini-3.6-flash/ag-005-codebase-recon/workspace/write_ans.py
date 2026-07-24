import os

with open("answer.txt", "w") as f:
    f.write("tok_uf9pa9r3sk")

with open("answer.txt", "r") as f:
    content = repr(f.read())
    print(f"answer.txt content repr: {content}")
