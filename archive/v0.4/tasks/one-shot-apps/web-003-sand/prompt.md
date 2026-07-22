Build a **falling-sand cellular-automata sandbox** in a single self-contained
HTML file. Dark theme, centered canvas, material buttons — make it satisfying
to play with. The graded contract:

**Layout**
- `#sand` — the simulation canvas, rendered at **at least 400×400 CSS pixels**.
- Material selector buttons: `#mat-sand`, `#mat-water`, `#mat-wall`,
  `#mat-acid`, `#mat-empty` (eraser).
- `#clear` — button that empties the whole grid.
- Painting: mouse drag on the canvas paints the selected material.

**Simulation rules** (grid of at least 80×80 cells; each cell is exactly one
of `empty | sand | water | wall | acid`):
- **Sand** falls straight down one cell per step into `empty` (or swaps with
  `water`/`acid` — it sinks). If blocked below, it slides diagonally
  down-left/down-right (randomize the direction checked first). Otherwise it
  rests.
- **Water** falls like sand; when it can't fall it spreads horizontally into
  empty cells (randomize direction).
- **Acid** moves like water, and additionally **dissolves** `sand` or `wall`
  cells it touches below or beside (both the acid and the dissolved cell may
  disappear, or just the target — your choice, but walls must erode).
- **Walls** never move.
- **Critical:** process movement bottom-row-up each step so a particle moves
  at most one cell per step — no teleporting through the grid.
- The bottom row and side edges act as solid boundaries.

**Programmatic API — required for grading.** Expose on `window`:

```js
window.sim = {
  w, h,                 // grid size in cells (numbers)
  tick(n),              // advance the simulation n steps SYNCHRONOUSLY
  get(x, y),            // -> "empty"|"sand"|"water"|"wall"|"acid"
  set(x, y, material),  // place one cell (same material names)
  clear(),              // empty the whole grid (same as #clear)
}
```

`y = 0` is the **top** row; `y = h-1` is the bottom. The animation may run on
`requestAnimationFrame`, but `tick(n)` must work deterministically for tests.

Single file, all CSS/JS inline, no external resources. Every control must
actually work — no dead UI, no stub functions.
