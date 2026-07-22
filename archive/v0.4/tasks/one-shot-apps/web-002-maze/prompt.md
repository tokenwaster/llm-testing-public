Build a **maze game with 24 autonomous pathfinding bots** in a single
self-contained HTML file. Make it look good (animated bots, visible walls,
clean HUD) — but the graded contract below must match exactly:

**Layout & controls**
- `#maze` — the rendered maze (canvas or DOM grid, your choice). It must
  render at **at least 400×400 CSS pixels** with clearly visible walls and
  bots — if you use a `<canvas>`, size it explicitly (the browser default is
  a useless 300×150).
- `#completed` — HUD element whose text contains the number of bots that have
  reached the exit so far.
- `#timer` — HUD element showing elapsed time.
- `#reset` — button that restarts the game from scratch.

**Game rules**
- Generate a rectangular maze at least **15×15 cells** with internal walls,
  a spawn cell and an exit cell, guaranteed solvable (generate a perfect maze
  or verify connectivity).
- Spawn **24 bots** at the spawn cell. Each bot pathfinds to the exit
  (BFS / A* / your choice). Stagger or randomize them so they don't move as
  one blob — but every bot must eventually arrive.
- The HUD tallies completions and elapsed time; animation runs via
  `requestAnimationFrame` or a timer.

**Programmatic API — required for automated grading.** Expose on `window`:

```js
window.game = {
  bots,            // array, length 24; each bot has .x and .y cell coords
  completed,       // number of bots that reached the exit (or a getter)
  elapsedMs,       // elapsed play time in ms
  tick(n),         // advance the simulation n steps SYNCHRONOUSLY
                   //   (each step: every unfinished bot advances one cell)
  reset(),         // same effect as clicking #reset
}
```

`tick(n)` must be deterministic and synchronous so tests can fast-forward:
after `game.tick(5000)`, all 24 bots must have completed (`completed === 24`)
and `#completed` must show 24. After `reset()`, `completed` is 0, all bots are
back at spawn, and `tick` works again.

Single file, all CSS/JS inline, no external resources. Every control must
actually work — no dead UI, no stub functions, no placeholder features.
