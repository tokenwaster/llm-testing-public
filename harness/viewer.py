"""Read-only results viewer — the public `harness serve`.

Serves the generated static site (overview, per-run / per-task / per-model
pages, /info, /discriminate), the dataset switcher, and read-only browsing of
runs/. It has NO control surface: no /run, /watch, /backend, /manage, and no
POST endpoints — so a publicly-deployed instance can't spend a subscription or
mutate data. The private operator server (`review.py`, held back from the
export) is the full control panel; when it's present, `harness serve` uses it
instead (see __main__).

This module imports only the public instrument (config, report, archive). It
must never import a private module — `tests/test_boundary.py` enforces that.
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import config, report

_CONTROL_PATHS = {"/run", "/run/", "/watch", "/watch/", "/backend", "/backend/",
                  "/manage", "/manage/", "/families-edit", "/families-edit/",
                  "/organize", "/review", "/review/"}

_CONTROL_STUB = ("""<!doctype html><meta charset="utf-8">
<title>operator-only</title>
<body style="background:#0d0d0d;color:#c3c2b7;font:15px system-ui;padding:40px;max-width:640px">
<h2 style="color:#fff">Operator-only page</h2>
<p>This is the <b>read-only results viewer</b>. The run / watch / backend /
manage control panel is part of the private operator layer and isn't served
here.</p>
<p>Everything on the <a style="color:#3987e5" href="/">overview</a> — the
leaderboard, per-task and per-model reports, the discrimination analysis, and
the raw run data — is available and reproducible: clone the harness, add your
own models, and run the same tasks.</p>
<p><a style="color:#3987e5" href="/">&larr; back to results</a></p></body>"""
                 ).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, code: int, body: bytes, ctype="text/html; charset=utf-8"):
        try:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

    def _send_file(self, rel: str):
        target = (config.REPORTS_DIR / rel).resolve()
        if not str(target).startswith(str(config.REPORTS_DIR.resolve())) \
                or not target.is_file():
            self._send(404, b"not found")
            return
        self._send(200, target.read_bytes())

    CTYPES = {".html": "text/html; charset=utf-8",
              ".json": "text/plain; charset=utf-8",
              ".jsonl": "text/plain; charset=utf-8",
              ".md": "text/plain; charset=utf-8",
              ".py": "text/plain; charset=utf-8",
              ".txt": "text/plain; charset=utf-8",
              ".csv": "text/plain; charset=utf-8",
              ".log": "text/plain; charset=utf-8"}

    def _send_run_data(self, rel: str):
        """Read-only browse of runs/ — transcripts, metrics, and each model's
        workspace (so a generated app.html opens live in a tab)."""
        from urllib.parse import quote, unquote
        rel = unquote(rel).strip("/")
        resolved = config.resolve_run_data(rel)
        if resolved is None:
            self._send(404, b"not found")
            return
        base, rel = resolved
        root = base.resolve()
        target = (base / rel).resolve() if rel else root
        if not str(target).startswith(str(root)):
            self._send(404, b"not found")
            return
        if target.is_dir():
            rows = []
            for p in sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name)):
                href = "/data/" + quote(str(p.relative_to(root)).replace("\\", "/"))
                rows.append(f'<li><a href="{href}{"/" if p.is_dir() else ""}">'
                            f'{p.name}{"/" if p.is_dir() else ""}</a>'
                            + ("" if p.is_dir() else
                               f' <small>({p.stat().st_size:,} B)</small>') + "</li>")
            up = "/data/" + quote(str(target.parent.relative_to(root)).replace("\\", "/")) \
                if target != root else None
            page = ("<!doctype html><meta charset='utf-8'>"
                    "<body style='background:#0d0d0d;color:#c3c2b7;"
                    "font:14px system-ui;padding:24px'>"
                    f"<h3 style='color:#fff'>runs/{rel}</h3>"
                    + (f'<p><a style="color:#3987e5" href="{up}/">⬆ up</a></p>' if up else "")
                    + f"<ul>{''.join(rows) or '(empty)'}</ul>"
                    "<style>a{color:#3987e5;text-decoration:none}</style></body>")
            self._send(200, page.encode("utf-8"))
        elif target.is_file():
            ctype = self.CTYPES.get(target.suffix.lower(), "application/octet-stream")
            self._send(200, target.read_bytes(), ctype)
        else:
            self._send(404, b"not found")

    def _json(self, code: int, data) -> None:
        self._send(code, json.dumps(data).encode(), "application/json")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._send_file("index.html")
        elif path in ("/info", "/info/", "/info.html"):
            self._send_file("info.html")
        elif path in ("/discriminate", "/discriminate/", "/discriminate.html"):
            self._send_file("discriminate.html")
        elif path in ("/family", "/family/", "/families", "/family.html"):
            self._send_file("family.html")
        elif path in ("/compare", "/compare/", "/compare.html"):
            self._send_file("compare.html")
        elif path in ("/special", "/special/", "/special.html"):
            self._send_file("special.html")
        elif path == "/feed.xml":
            p = config.REPORTS_DIR / "feed.xml"
            if p.is_file():
                self._send(200, p.read_bytes(),
                           "application/atom+xml; charset=utf-8")
            else:
                self._send(404, b"not found")
        elif path.startswith(("/runs/", "/tasks/", "/models/", "/datasets/")) \
                and path.endswith(".html"):
            rel = path.lstrip("/")
            if rel.startswith("datasets/") \
                    and not (config.REPORTS_DIR / rel).is_file():
                import re as _re
                m = _re.match(r"datasets/v(\d+\.\d+)/", rel)
                if m:
                    try:
                        from .archive import render_dataset
                        render_dataset(m.group(1), progress=lambda *_: None)
                    except FileNotFoundError:
                        pass
            self._send_file(rel)
        elif path == "/api/versions":
            from .archive import list_archives
            self._json(200, {"live": config.suite_version(),
                             "archives": list_archives()})
        elif path.startswith("/data/") or path == "/data":
            self._send_run_data(path[len("/data"):])
        elif path in _CONTROL_PATHS:
            self._send(200, _CONTROL_STUB)
        else:
            self._send(404, b"not found")

    def do_POST(self):
        self._send(405, b"read-only viewer: control actions are operator-only")


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        import sys
        exc = sys.exception()
        if isinstance(exc, (ConnectionAbortedError, ConnectionResetError,
                            BrokenPipeError, TimeoutError)):
            return
        super().handle_error(request, client_address)


def serve(port: int | None = None) -> None:
    port = config.serve_port() if port is None else port
    report.generate_all(public_nav=True)
    server = QuietServer(("127.0.0.1", port), Handler)
    print(f"LLM Testing Suite  v{config.suite_version()}  (read-only viewer)")
    print(f"Results:  http://127.0.0.1:{port}")
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
