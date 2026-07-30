Build a single self-contained `app.html` — a **playable** top-down **billiards
game** with a correct 2D physics simulation. No external files, no network;
inline all CSS and JS. Render the table and balls on a `<canvas>`.

**It must be playable.** A player must be able to **aim and shoot the cue ball
with the mouse**: press on the white cue ball, drag *back* to set direction and
power, and release to strike (longer drag = harder shot). Provide a **Reset /
rack** control that returns the balls to a starting layout, and show **visible
on-screen instructions** telling the player how to shoot. An implementation that
cannot actually be played — no way to shoot the cue ball, or no reset — does not
satisfy this task, regardless of how good the physics is.

The simulation is graded programmatically, so it must expose a global
`window.sim` object with **exactly** this contract:

- `window.sim.W`, `window.sim.H` — playfield size in pixels (numbers).
- `window.sim.R` — ball radius in pixels (number).
- `window.sim.reset(balls)` — place balls. `balls` is an array of
  `{x, y, vx, vy, cue}` (velocity px/sec, may be omitted → 0; `cue: true` marks
  the cue ball). Order is preserved.
- `window.sim.step(dt)` — advance the physics by `dt` seconds, then redraw.
- `window.sim.state()` — array, same order as `reset`, of
  `{x, y, vx, vy, potted, cue}` for every ball.
- `window.sim.shoot(vx, vy)` — give the cue ball this velocity (the same effect
  your mouse control produces).
- `window.sim.pause()` / `window.sim.resume()` — stop / start the animation
  loop, so the physics can be stepped deterministically for grading.

Physics requirements (all measured):

1. **Motion & friction.** Balls move by their velocity; a rolling ball loses
   speed smoothly and comes to rest; speed never increases on its own.
2. **Cushions.** Balls reflect off the four walls and stay within `R … W-R`,
   `R … H-R`.
3. **Ball-to-ball collisions.** Equal-mass, (near-)elastic, resolved along the
   line joining centres: a head-on shot into a resting ball drives it forward
   while the striker sheds speed. Momentum and kinetic energy are conserved
   (energy may only decrease).
4. **Pockets.** Six pockets (four corners + the middle of each long rail). A
   ball whose centre reaches a pocket is **potted** (`potted: true`, out of play).
5. **Deterministic.** The same `reset` + `step` sequence always produces the
   same `state()`.

Make it look and feel like a real table (felt, rails, pockets, an aim line while
you drag) — but the score comes from the physics *and* from the game actually
being playable.
