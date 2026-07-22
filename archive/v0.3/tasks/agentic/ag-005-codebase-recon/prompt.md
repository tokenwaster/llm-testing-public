Your workspace contains a Python package `pipeline/` with 30 handler modules
plus `entry.py`.

- `entry.py` defines `START` — the name of the first module in the dispatch
  chain.
- Every module defines `NEXT` — the name of the module it forwards to
  (or `None` at the end of a chain).
- Every module also defines a `SECRET_TOKEN`. **Every module has one**, so
  searching for the constant name tells you nothing — the only way to find the
  right one is to actually follow the chain.

Starting at the module named by `START`, follow `NEXT` hop by hop until you
have visited **7 modules in total** (the start module counts as the 1st).

Write the `SECRET_TOKEN` of that 7th module into a file called `answer.txt`
in your workspace root — the token value only, nothing else.

You may read files one by one or write a small script to walk the chain —
your choice. Verify before finishing.
