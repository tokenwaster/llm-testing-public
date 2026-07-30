Build a mini spreadsheet as a single self-contained web app.

Grid: 10 columns (A–J) × 10 rows (1–10). Every cell is an `<input>` element
with id `cell-A1` … `cell-J10`, laid out as a proper grid with row/column
headers. The visible app must be at least 600×400 px.

Behavior:
- A cell holds either a plain value or a formula starting with `=`.
- Formulas support numbers, cell references (`A1`), `+ - * /`, and
  parentheses, with normal operator precedence: `=2+3*4` is 14,
  `=(2+3)*4` is 20, `=A1*2+B2` works.
- When a cell is not being edited it displays its COMPUTED value; clicking
  into it shows the raw text for editing; Enter or clicking away commits.
- Recalculation is automatic and transitive: changing `A1` immediately
  updates every cell whose formula depends on it, directly or through other
  cells.
- Circular references display exactly `#CYCLE` in every cell of the cycle.
- Invalid formulas (bad syntax, reference to a non-cell) display `#ERR`.
- Non-numeric plain text displays as itself; empty cells count as 0 inside
  formulas.
- An **Export CSV** button with id `export` writes the current 10×10 grid of
  COMPUTED values into a `<textarea id="csv">` (comma-separated, one line
  per row).

Scripting API (for automated grading — must work exactly as specified):

    window.sheet.set("B2", "=A1*2")   // enter text into a cell, as if typed
    window.sheet.get("B2")            // -> the DISPLAYED string, e.g. "10"
    window.sheet.raw("B2")            // -> the raw text, e.g. "=A1*2"

No dead UI: every visible control must actually work. No external resources.
