Your workspace contains `data.csv` — a messy export of user signups. Clean it
and write the result to `output.json` in your workspace. You may write any
helper scripts you like; only `output.json` is graded.

Cleaning rules, applied in this order:

1. **Drop invalid rows**: a row is invalid if its email contains no `@`, its
   email is empty, or its score is empty.
2. **Normalize emails** to lowercase.
3. **Normalize dates**: `signup` values are either `YYYY-MM-DD` (keep as is)
   or `DD/MM/YYYY` (convert). Output format is always `YYYY-MM-DD`.
4. **Deduplicate by email**: when the same (normalized) email appears more
   than once, keep only the row with the **highest score** (scores are unique
   per email, no ties).
5. **Sort** the remaining records by email, ascending.

`output.json` must be a JSON array of objects, each with exactly these keys:
`"email"` (string), `"signup"` (string, `YYYY-MM-DD`), `"score"` (integer).

Verify your output by running your script and inspecting the file before
finishing.
