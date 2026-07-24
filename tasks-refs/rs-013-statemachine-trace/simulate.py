"""Author + simulate the rs-013 stack machine. Deterministic, no underflow by
construction. Prints the five checkpoint answers and the program listing."""


PROG = [
    "PUSH 6", "PUSH 5", "PUSH 9", "DUP", "TICK",
    "PUSH 4", "ADD", "STORE", "LOAD", "MUL",
    "PUSH 7", "NEG", "ADD", "SWAP", "POP",
    "PUSH 2", "TICK", "PUSH 3", "POP", "DUP",
    "ADD", "PUSH 8", "SWAP", "STORE", "TICK",
    "LOAD", "ADD", "PUSH 1", "POP", "NEG",
    "PUSH 10", "ADD", "DUP", "MUL", "TICK",
    "PUSH 5", "SWAP", "POP", "LOAD", "ADD",
]


def run(prog):
    st, R, odd_pops, max_top = [], 0, 0, None
    for ins in prog:
        op, *rest = ins.split()
        if op == "PUSH":
            st.append(int(rest[0]))
        elif op == "POP":
            v = st.pop()
            if v % 2 != 0:
                odd_pops += 1
        elif op == "ADD":
            a = st.pop(); b = st.pop(); s = a + b
            st.append(0 if s < 0 else s)
        elif op == "MUL":
            a = st.pop(); b = st.pop(); st.append(a * b)
        elif op == "DUP":
            st.append(st[-1])
        elif op == "SWAP":
            st[-1], st[-2] = st[-2], st[-1]
        elif op == "NEG":
            st[-1] = -st[-1]
        elif op == "STORE":
            R = st[-1]
        elif op == "LOAD":
            st.append(R)
        elif op == "TICK":
            if st[-1] % 2 == 0:
                R += 1
            else:
                st.pop()
        else:
            raise ValueError(ins)
        if st:
            top = st[-1]
            max_top = top if max_top is None else max(max_top, top)
    return st, R, odd_pops, max_top


st, R, odd_pops, max_top = run(PROG)
print("FINAL_STACK (top->bottom):", ",".join(str(x) for x in reversed(st)))
print("MAX_TOP:", max_top)
print("REG_R:", R)
print("ODD_POPS:", odd_pops)
print("SUM_FINAL:", sum(st))
print("stack depth:", len(st))
