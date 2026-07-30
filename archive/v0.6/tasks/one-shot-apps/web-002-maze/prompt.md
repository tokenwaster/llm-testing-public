Build a maze game as a single self-contained web app: a randomly generated
perfect maze (at least 15×15 cells) with 24 bots that must **DISCOVER** the
exit — they do not know the maze layout or the exit location in advance.

**Exploration rules (the heart of this task):**
- Each bot starts knowing only its own cell. It learns walls and passages by
  moving through the maze, one cell per tick.
- Bots must explore like Tremaux/DFS: when a bot hits a dead end (or a fully
  explored branch), it BACKTRACKS and records that branch in its own memory
  as dead, and never fully re-explores it — no passage should be traversed
  more than twice by the same bot.
- Bots must NOT compute a path using global maze knowledge (no BFS/A* over
  the full maze). Give bots different exploration preferences (e.g. seeded
  direction orders) so they spread out.
- When a bot reaches the exit it stops there; the tick a bot arrives is its
  finish tick.
- A visible timer runs while any bot is still searching and **FREEZES at
  the moment the LAST bot arrives** — after that, further ticks must not
  change the timer or `game.elapsed`.

**Rendering:** canvas or DOM at least 400×400 px, walls clearly drawn, bots
as distinct colored dots that move SMOOTHLY (interpolated between cells, not
teleporting), staying centered in corridors. Show a completed-count (id
`completed`), the timer (id `timer`), a reset button (id `reset`), and the
maze itself inside an element with id `maze`.

**Scripting API (for automated grading — exactly as specified):**

    window.game.tick(n)      // advance the simulation n ticks, synchronously
    window.game.reset(seed?) // new maze, bots at spawn, elapsed = 0.
                             // With a numeric seed: the SAME seed must
                             // reproduce the identical maze and bot runs.
    window.game.elapsed      // ticks elapsed; STOPS at the last arrival
    window.game.size         // {rows, cols}
    window.game.spawn        // {r, c}
    window.game.exit         // {r, c}
    window.game.walls(r, c)  // {n, e, s, w} booleans for that cell
    window.game.bots         // array of 24 bot objects:
      bot.path       // every cell the bot has entered, in order: [{r,c}, ...]
      bot.deadEnds   // cells the bot marked as dead: [{r,c}, ...]
      bot.finishTick // null until arrival, then the tick number

`tick(n)` must be deterministic for a given maze: calling `tick(1)` n times
equals calling `tick(n)` once. All 24 bots must reach the exit within 20,000
ticks. No dead UI; no external resources.
