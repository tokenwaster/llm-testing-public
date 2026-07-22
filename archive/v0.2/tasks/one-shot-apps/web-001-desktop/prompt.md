Build a **desktop environment** in a single self-contained HTML file — visually
inspired by Ubuntu (dark theme, top bar or dock, desktop wallpaper area,
draggable-looking windows). Polish matters, but the following contract is what
gets graded, exactly as specified — element IDs and behaviors must match:

**Shell**
- `#desktop` — the desktop root element, filling the browser viewport.
- `#taskbar` — a taskbar/dock containing two launcher buttons:
  `#open-files` and `#open-notepad`.
- App windows must open at a **usable size — at least 360×240 CSS pixels** —
  with their content visible, not collapsed or zero-height.
- Clicking a launcher shows its window: `#files-window` / `#notepad-window`.
  Each window has a close button with class `.win-close` that hides it
  (display none or removed from view). Windows can be reopened any number of
  times.

**Files app** (a browsable replica of a Linux filesystem — static fake data)
- `#files-path` shows the current absolute path, starting at `/`.
- Every file/folder in the listing is an element with class `.fs-item`; its
  visible text is the entry name.
- The root `/` must contain at least: `bin`, `etc`, `home`, `usr`, `var`.
- `/home` contains `user`; `/home/user` contains at least `Documents`,
  `Downloads`, `Pictures` (plus any files you like).
- **Double-clicking** a folder navigates into it (path updates); `#files-up`
  navigates to the parent. Deeper structure beyond the required paths is
  welcome.

**Notepad app** (tabbed, persistent)
- `#tabs` holds the tab strip; each tab is an element with class `.tab`.
- `#new-tab` creates a new empty tab and makes it active.
- `#editor` is a `<textarea>` showing the active tab's content; clicking a
  `.tab` switches to it.
- All tabs and their content **persist in `localStorage`**: closing the
  notepad window and reopening it — or reloading the whole page — restores
  every tab and its text exactly.

Single file, all CSS/JS inline, no external resources, no frameworks required
(vanilla JS is fine).
