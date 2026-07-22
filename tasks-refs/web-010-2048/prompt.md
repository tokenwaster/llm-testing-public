Build the game **2048** as a single self-contained HTML file. Dark theme, a
centered 4×4 board, a visible score, arrow-key control. The graded contract:

**Layout**
- `#board` — the 4×4 grid, showing each tile's number.
- `#score` — element showing the current score.
- `#reset` — button that starts a new game.
- Arrow keys move the tiles.

**Rules** (4×4 grid; empty cells are 0):
- A move slides all tiles as far as they go in that direction. Two tiles with
  the **same value that collide merge into one** of double the value, and the
  merged value is **added to the score**.
- Each tile can merge **at most once per move** — `[2,2,2,2]` moved left becomes
  `[4,4,0,0]`, never `[8,0,0,0]`.
- After any move that changed the board, a new tile (2, occasionally 4) appears
  on a random empty cell. A move that changes nothing spawns nothing.
- A new game starts with exactly **2 tiles** and score 0.

**Programmatic API — required for grading.** Expose on `window`:

```js
window.game = {
  size,                 // 4
  reset(),              // new game: 2 tiles, score 0
  move('left'|'right'|'up'|'down'),  // -> boolean: did anything move?
  board(),              // -> 4x4 array of numbers (0 = empty)
  setBoard(arr),        // set the grid exactly (no spawn) — used by grading
  score(),              // -> number
};
```

Grading sets known boards via `setBoard` and checks the slide/merge results,
the score, that a tile never double-merges, and that `move()` returns false when
nothing changes. Tile numbers must be visible in `#board`.
