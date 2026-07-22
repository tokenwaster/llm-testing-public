Build the game **Snake** as a single self-contained HTML file. Dark theme,
centered board, arrow-key control, a visible score. The graded contract:

**Layout**
- `#snake` — the game board canvas, rendered at **at least 400×400 CSS pixels**.
- Buttons: `#start` (begin auto-advancing), `#pause`, `#reset`.
- A `#score` element showing the current score.
- Arrow keys steer the snake.

**Rules** (grid of at least **10×10** cells):
- The snake starts length ≥ 3 and moves one cell per tick in its current
  direction. Eating the food grows the snake by one and increments the score,
  then new food appears on a free cell.
- Running into a **wall** ends the game. Running into **its own body** ends the
  game.
- A **180° reversal** (e.g. turning left while moving right) is ignored — the
  snake keeps its heading.

**Programmatic API — required for grading.** Expose on `window`:

```js
window.game = {
  w, h,                 // board size in cells (>= 10)
  reset(),              // new game: snake length >= 3, alive, score 0
  tick(),               // advance exactly one step
  setDir('up'|'down'|'left'|'right'),   // queue a turn (ignore 180° reversals)
  setFood(x, y),        // place the food (used by grading; also redraw)
  snake(),              // -> array of [x,y], HEAD FIRST
  food(),               // -> [x,y]
  alive(),              // -> boolean
  score(),              // -> number
};
```

Grading drives this API: it feeds the snake to make it grow, runs it into a
wall and into itself (both must end the game), and checks that a reversal is
ignored. The snake and food must be visibly drawn. Make it feel good to play.
