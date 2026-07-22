Build **Conway's Game of Life** as a single self-contained HTML file. Dark
theme, centered grid, playful controls. The graded contract:

**Layout**
- `#life` — the grid canvas, rendered at **at least 400×400 CSS pixels**.
- Buttons: `#step` (advance one generation), `#play` (toggle auto-run),
  `#random` (seed random cells), `#clear` (kill all cells).
- Clicking / dragging on the grid toggles cells (paint alive/dead).

**Simulation** (grid of at least **40×40** cells; each cell is alive `1` or
dead `0`):
- Standard **B3/S23** rules: a dead cell with exactly 3 live neighbours becomes
  alive; a live cell with 2 or 3 live neighbours survives; otherwise it dies.
- Neighbours are the 8 surrounding cells. **Edges are dead** — cells outside the
  grid count as 0 (no wrap-around).
- **Critical:** each generation is computed **simultaneously** — the next state
  of every cell is derived from the *current* generation, then applied all at
  once. Updating cells in place (so later cells see already-updated neighbours)
  is wrong and will fail the oscillator/glider tests.

**Programmatic API — required for grading.** Expose on `window`:

```js
window.life = {
  w, h,                 // grid dimensions in cells (>= 40 each)
  get(x, y),            // -> 0 or 1  (0 for out-of-bounds)
  set(x, y, v),         // set cell (x,y) alive (truthy) or dead
  step(),               // advance exactly one generation (and redraw)
  clear(),              // set every cell dead (and redraw)
};
```

Grading drives this API: it seeds known patterns and checks their evolution — a
2×2 block stays put, a 3-cell blinker rotates each step, a lone cell dies, and a
glider advances by (+1,+1) every 4 steps. Live cells must be visibly drawn on
the grid. Make it fun to watch.
