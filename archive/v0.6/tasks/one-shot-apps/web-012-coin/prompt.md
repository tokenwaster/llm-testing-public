I need an amazing, impressive, extraordinary website for **WastedToken Mint**, a
company that mints collectible physical challenge coins.

Deliver **one self-contained `app.html`**. No external dependencies, no network
calls, no external image or asset URLs — every visual is procedural or inline.
Complete the entire project in one pass, no questions.

## Hero — the coin

A single large challenge coin, rendered and animated entirely by you. WebGL,
Three.js (inlined), or 2D canvas — your choice. The coin must:

- **Rotate in 3D about the vertical axis AND flip about the horizontal axis**, so
  both faces are seen during one loop.
- Show a **front face** embossed with the WastedToken Mint emblem in raised
  relief, and a **back face** showing a denomination as a token count (e.g.
  "10,000 TOKENS"). The two faces must look clearly different.
- Have a **reeded (ridged) edge** visible as the coin turns.
- Use a **metallic finish with a specular highlight that visibly rakes across the
  surface as it rotates**. A flat or matte disc is a fail.

## Below the hero

- An **About** section for the mint, with plausible on-brand copy.
- A **collection grid of exactly 4 coin editions**, each procedurally rendered in
  the same style — no placeholder boxes, no grey rectangles:
  1. **Bronze** — available
  2. **Silver** — available
  3. **Gold** — SOLD OUT: visually distinct and not purchasable
  4. **Black (obsidian)** — MINTING NEXT SEASON: name the season, not purchasable

## Required markup — grading depends on it

The hero canvas must be `<canvas id="coin-hero">`.

Each edition tile:

```html
<div class="edition" data-edition="bronze|silver|gold|black"
     data-state="available|sold-out|coming-soon">
  <canvas class="edition-canvas"></canvas>
  <button class="buy">Add to cart</button>   <!-- available editions ONLY -->
</div>
```

- Exactly 4 `.edition` tiles, one per `data-edition` value above.
- Available tiles carry an enabled `button.buy`. Sold-out and coming-soon tiles
  must have **no enabled `button.buy`**.
- The sold-out tile's text must contain "SOLD OUT". The coming-soon tile's text
  must name the season (spring / summer / autumn / fall / winter).

## Programmatic API — required for grading

```js
window.demo = {
  canvas,        // the hero <canvas> element
  setTime(t),    // t in [0,1] -> render EXACTLY that point of the loop,
                 // synchronously. Deterministic: the same t must always
                 // produce the same pixels.
  pause(),       // stop the animation loop (grading calls this first)
};
```

Grading pauses the animation, steps `setTime` across the loop, and analyses the
**rendered pixels**: the coin's silhouette through the turn, whether both faces
actually appear, and whether a specular highlight genuinely moves. Plausible
shader code that renders to a flat grey disc scores zero here — the render is
judged from output, never from source.

So the coin stays measurable: the hero canvas must contain **only the coin** on a
simple backdrop, and the coin must not touch the canvas edges.

Everything else — layout, type, palette, copy, motion design — is yours. This
ships to the real internet: CEOs, collectors, and the entire troll kingdom will
see it and criticise it. This is our only shot.
