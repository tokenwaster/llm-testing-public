import subprocess, sys, os, textwrap

def run(content, name):
    with open(name, "w") as f:
        f.write(content)
    out = subprocess.run([sys.executable, "wordstats.py", name],
                         capture_output=True, text=True)
    print(repr(content), "->", repr(out.stdout), "rc=", out.returncode)

run("", "t_empty.txt")                      # empty file: 0 lines, 0 words, top - 0
run("123 456 _ !!!\n", "t_noword.txt")      # no words
run("no trailing newline", "t_notrail.txt") # 1 line
run("a\n", "t_trail.txt")                   # 1 line
run("b a b a\n", "t_tie.txt")               # tie -> 'a' 2
run("Zebra apple Apple zebra ZEBRA\n", "t_case.txt")  # zebra 3
run("one\ntwo\nthree\n", "t_lines.txt")     # 3 lines, 3 words, top 'one' 1
