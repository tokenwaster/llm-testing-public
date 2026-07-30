Build a **bouncing-ball physics playground** in a single self-contained HTML
file. Dark theme, centered canvas, satisfying to click. The graded contract:

**Layout**
- `#sim` — the simulation canvas, rendered at **at least 400×400 CSS pixels**.
- Buttons: `#drop` (drop a new ball), `#play` (toggle animation), `#clear`
  (remove all balls).
- Clicking the canvas adds a ball at the cursor.

**Physics** — balls are circles with position `(x,y)`, velocity `(vx,vy)`, and a
radius `r`:
- **Gravity** accelerates every ball downward each step (increase `vy`).
- A ball **bounces** off the four canvas edges: when it reaches an edge, clamp
  it inside and reverse the perpendicular velocity component (a little energy
  loss is fine, i.e. multiply by a restitution < 1).
- Balls must **stay within the canvas** — never tunnel through an edge.

**Programmatic API — required for grading.** Expose on `window`:

```js
window.sim = {
  w, h,                          // canvas size in pixels
  balls(),                       // -> [{x, y, vx, vy, r}, ...]
  addBall(x, y, vx=0, vy=0, r?), // add a ball
  clear(),                       // remove all balls
  step(dt=1),                    // advance the simulation one step (and redraw)
};
```

Grading drives this API: it releases a ball and checks it accelerates down,
bounces off the floor (velocity reverses, ball stays in bounds), bounces off a
wall, and that balls never escape the canvas over a long run. Balls must be
visibly drawn.
