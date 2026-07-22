"""Sandbox tools for tier-2 agentic tasks. Every operation is confined to the
task's workspace directory — path escapes are rejected."""

import sys
from pathlib import Path

from . import config
from .util import run_capped, truncate

TOOL_DEFS = [
    {
        "name": "list_files",
        "description": "List all files in your workspace (recursive), with sizes.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_file",
        "description": "Read a text file from your workspace. Path is relative to the workspace root.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Relative path, e.g. 'main.py'"},
        }, "required": ["path"]},
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a text file in your workspace. Parent directories are created automatically.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Relative path, e.g. 'solution.py'"},
            "content": {"type": "string", "description": "Full file content"},
        }, "required": ["path", "content"]},
    },
    {
        "name": "run_python",
        "description": ("Run a Python file from your workspace and get its stdout/stderr and exit code. "
                        "Use this to test your work before finishing."),
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Relative path of the .py file to run"},
            "args": {"type": "array", "items": {"type": "string"},
                     "description": "Optional command-line arguments"},
        }, "required": ["path"]},
    },
]


def _resolve(workspace: Path, rel: str) -> Path:
    p = (workspace / rel).resolve()
    if not str(p).startswith(str(workspace.resolve())):
        raise ValueError(f"path escapes workspace: {rel}")
    return p


def execute_tool(workspace: Path, name: str, args: dict) -> str:
    """Execute a tool call; always returns a string (errors included) so the
    model can react rather than the run crashing."""
    try:
        if name == "list_files":
            files = sorted(p for p in workspace.rglob("*") if p.is_file())
            if not files:
                return "(workspace is empty)"
            return "\n".join(
                f"{p.relative_to(workspace)} ({p.stat().st_size} bytes)" for p in files)

        if name == "read_file":
            p = _resolve(workspace, args["path"])
            if not p.exists():
                return f"ERROR: file not found: {args['path']}"
            return truncate(p.read_text(encoding="utf-8", errors="replace"),
                            config.TOOL_OUTPUT_LIMIT)

        if name == "write_file":
            p = _resolve(workspace, args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"], encoding="utf-8")
            return f"OK: wrote {len(args['content'])} chars to {args['path']}"

        if name == "run_python":
            p = _resolve(workspace, args["path"])
            if not p.exists():
                return f"ERROR: file not found: {args['path']}"
            cmd = [sys.executable, str(p)] + [str(a) for a in (args.get("args") or [])]
            proc = run_capped(
                cmd, config.TOOL_RUN_TIMEOUT_S, cwd=str(workspace), text=True,
                encoding="utf-8", errors="replace")
            if proc.timed_out:
                return f"ERROR: timed out after {config.TOOL_RUN_TIMEOUT_S}s"
            out = f"exit code: {proc.returncode}\n"
            if proc.stdout:
                out += f"--- stdout ---\n{proc.stdout}\n"
            if proc.stderr:
                out += f"--- stderr ---\n{proc.stderr}\n"
            return truncate(out, config.TOOL_OUTPUT_LIMIT)

        return f"ERROR: unknown tool '{name}'"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"
