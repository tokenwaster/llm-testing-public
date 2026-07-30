Build a **personal expense tracker** in a single self-contained HTML file.
Working features and clear UX over visual flair. The graded contract:

**Entry form**
- `#amount` (number input), `#category` (a `<select>` containing at least the
  options `groceries`, `transport`, `bills`, `fun`), `#date` (date input),
  `#note` (optional text), and `#add-expense` (submit button).
- **Validation:** an empty, non-numeric, zero, or negative amount — or a
  missing date — must NOT add an expense; instead show a message in
  `#form-error` (non-empty text). A valid submission clears `#form-error`
  and resets the amount field.

**List & summary**
- Each expense is a row with class `.expense`, newest first, showing amount,
  category, and date; each row has a delete button with class `.exp-del`
  (immediate, no confirm dialog).
- `#total` shows the sum of the **currently visible** (filtered) expenses,
  formatted with two decimals (e.g. `74.50`).
- A per-category summary: one element per category with class `.cat-total`
  and attribute `data-cat="<category>"` whose text contains that category's
  visible total.

**Filters (combinable)**
- `#filter-category` — a `<select>` with `all` plus the categories; picking
  one hides non-matching rows.
- `#filter-from` and `#filter-to` — date inputs; rows outside the range hide.
  Category + date filters apply **together**, and `#total` always reflects
  what's visible.

**Persistence**
- Expenses persist in `localStorage` — reload restores the full list.

Vanilla HTML/CSS/JS in one file, no external resources. Every control must
actually work — no dead UI, no stub functions.
