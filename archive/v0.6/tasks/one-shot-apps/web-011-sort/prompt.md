Build a **sorting-algorithm visualizer** in a single self-contained HTML file.
Dark theme, an array shown as vertical bars, animated sorting. The graded
contract:

**Layout**
- `#bars` — the container showing the array as bars (height ∝ value); each bar
  is an element with class `bar`.
- Buttons: `#sort` (animate the sort to completion), `#shuffle` (randomize the
  array), `#reset`.

**Behaviour**
- Sort **ascending**. You may use any comparison sort, but it must be driven one
  step at a time by the API below (so it can be animated) — not a single
  `Array.sort()` call.
- `sortStep()` performs exactly one comparison/step of the sort and returns
  `true` once the array is fully sorted, `false` otherwise. Repeatedly calling it
  must eventually sort the array (a permutation of the input, ascending).

**Programmatic API — required for grading.** Expose on `window`:

```js
window.viz = {
  array(),          // -> current array of numbers
  setArray(a),      // set the array (and redraw)
  sortStep(),       // advance the sort ONE step; -> true when fully sorted
  sorted(),         // -> boolean: is the array ascending?
};
```

Grading sets a known shuffled array, calls `sortStep()` until `sorted()` is
true, and checks the result is that array sorted ascending. The bars must be
rendered (one `.bar` per element).
