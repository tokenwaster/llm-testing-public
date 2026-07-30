You are a deterministic stack machine. Execute the program below one instruction
at a time, exactly as specified, and report the final state.

## Machine

- A **stack** of integers (the *top* is the most recently pushed value).
- One **register R**, an integer, starting at `0`.
- Two counters you must track: **odd_pops** (starts 0) and **max_top** (the
  largest value that is ever on top of the stack immediately *after* any
  instruction, considering only moments when the stack is non-empty).

## Instructions

- `PUSH k` — push the integer `k`.
- `POP` — remove the top value. If the value removed is **odd**, add 1 to **odd_pops**.
- `ADD` — pop `a` (top), pop `b` (next), push `a + b`. **However, if `a + b` is
  negative, push `0` instead.**
- `MUL` — pop `a`, pop `b`, push `a * b`.
- `DUP` — push a copy of the current top value.
- `SWAP` — exchange the top two values.
- `NEG` — replace the top value with its negation.
- `STORE` — copy the top value into `R`. The top value is **not** removed.
- `LOAD` — push the current value of `R`.
- `TICK` — look at the top value. If it is **even**, do `R = R + 1` and leave the
  stack unchanged. If it is **odd**, remove the top value. (A value removed by
  `TICK` does **not** count toward odd_pops — only `POP` counts.)

The program is constructed so the stack never underflows.

## Program

```
1  PUSH 6      11 PUSH 7      21 ADD        31 PUSH 10
2  PUSH 5      12 NEG         22 PUSH 8     32 ADD
3  PUSH 9      13 ADD         23 SWAP       33 DUP
4  DUP         14 SWAP        24 STORE      34 MUL
5  TICK        15 POP         25 TICK       35 TICK
6  PUSH 4      16 PUSH 2      26 LOAD       36 PUSH 5
7  ADD         17 TICK        27 ADD        37 SWAP
8  STORE       18 PUSH 3      28 PUSH 1     38 POP
9  LOAD        19 POP         29 POP        39 LOAD
10 MUL         20 DUP         30 NEG        40 ADD
```

## Output

Think step by step if you wish, but end your reply with **exactly** these five
lines and nothing after them. `FINAL_STACK` is listed **top first**, comma-
separated, no spaces:

```
FINAL_STACK: <values top->bottom>
MAX_TOP: <integer>
REG_R: <integer>
ODD_POPS: <integer>
SUM_FINAL: <integer>
```
