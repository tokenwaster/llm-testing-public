Build a **kanban board** in a single self-contained HTML file. Clean, modern
column layout; cards should feel like cards. The graded contract:

**Board**
- Three columns with ids `#col-todo`, `#col-doing`, `#col-done`, each with a
  visible header and a card container.
- Each column header shows a live count of its cards in an element with class
  `.count` inside that column.

**Cards**
- `#new-card` — a text input; `#add-card` — a button that creates a card in
  **To Do** from the input's text (and clears the input). Empty input adds
  nothing.
- Every card is an element with class `.card` whose visible text includes its
  title, plus a delete button with class `.card-del` (deletes immediately —
  no confirm dialog).
- Cards are **draggable between columns with HTML5 drag-and-drop**
  (`draggable="true"`, proper `dragstart`/`dragover`/`drop` handlers on the
  columns). Dropping a card on a column moves it there and updates both
  counts.

**Persistence**
- The full board state (cards + which column each is in) persists in
  `localStorage`: a page reload restores every card to the right column.

Single file, all CSS/JS inline, no external resources. Every control must
actually work — no dead UI, no stub functions.
