
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from . import config, gguf, scoring
from .adapters import (AdapterError, BaseAdapter, ChatResult, _fmt_epoch,
                       make_adapter)
from .registry import Model
from .tasks import Task
from .tools import TOOL_DEFS, execute_tool
from .util import append_jsonl, now_iso, now_ms, write_json


class RunInProgress(Exception):
    pass


class SpendRefused(Exception):
    pass


def active_run() -> str | None:
    from .util import read_json
    for base in (config.RUNS_DIR, getattr(config, "SCOUTS_DIR", None),
                 getattr(config, "SPECIAL_DIR", None),
                 getattr(config, "PRIVATE_RUNS_DIR", None)):
        if not base or not base.is_dir():
            continue
        for run_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            manifest = read_json(run_dir / "run.json", {})
            if manifest and not manifest.get("finished"):
                return run_dir.name
    return None


def _window_limited() -> dict[str, dict[str, str]]:
    from .util import read_json
    out: dict[str, dict[str, str]] = {}
    if not config.RUNS_DIR.is_dir():
        return {}
    for mfile in config.RUNS_DIR.glob("*/*/*/metrics.json"):
        d = read_json(mfile, {})
        if d.get("status") != "error":
            continue
        atts = d.get("attempts") or [{}]
        if atts[0].get("error_kind") == "rumination_spiral":
            reason = "silence"
        elif atts[-1].get("error_kind") == "timeout":
            reason = "timeout"
        else:
            continue
        model, task = mfile.parents[1].name, mfile.parent.name
        cur = out.setdefault(model, {})
        if cur.get(task) != "silence":
            cur[task] = reason
    return out


def spiral_matrix() -> dict[str, list[str]]:
    return {m: sorted(t) for m, t in sorted(_window_limited().items())}


def window_reasons() -> dict[str, dict[str, str]]:
    return _window_limited()


_WINDOW_NEED: dict | None = None


def measured_window_need(model: str, task: str) -> float | None:
    global _WINDOW_NEED
    if _WINDOW_NEED is None:
        import re
        from .util import read_json
        need: dict = {}
        base = getattr(config, "SPECIAL_DIR", None)
        if base and base.is_dir():
            probe_runs = {rj.parent.name for rj in base.glob("*/run.json")
                          if re.search(r"spiral@\d+s",
                                       read_json(rj, {}).get("tag") or "")}
            for mfile in base.glob("*/*/*/metrics.json"):
                if mfile.parents[2].name not in probe_runs:
                    continue
                d = read_json(mfile, {})
                ftm = next((a.get("first_text_ms")
                            for a in (d.get("attempts") or [])
                            if a.get("first_text_ms") is not None), None)
                if ftm is None:
                    continue
                key = (mfile.parents[1].name, mfile.parent.name)
                need[key] = max(need.get(key, 0.0), ftm / 1000)
        _WINDOW_NEED = need
    return _WINDOW_NEED.get((model, task))


def sampling_drift(models=None) -> dict[str, dict]:
    from .registry import load_models
    from .tasks import load_tasks
    from .util import read_json
    models = models or load_models(include_disabled=True)
    tasks = {t.id: t for t in load_tasks()}
    newest: dict[tuple, dict] = {}
    if config.RUNS_DIR.is_dir():
        for mfile in sorted(config.RUNS_DIR.glob("*/*/*/metrics.json")):
            key = (mfile.parents[1].name, mfile.parent.name)
            if key[1] in tasks:
                newest[key] = read_json(mfile, {})
    out = {}
    for m in models:
        mismatch, unverified, current = [], 0, 0
        for tid, task in tasks.items():
            d = newest.get((m.name, tid))
            if d is None:
                continue
            used = d.get("sampling_used")
            if used is None:
                unverified += 1
                continue
            want = m.sampling_payload(task.category)
            if used != want:
                mismatch.append(tid)
            else:
                current += 1
        out[m.name] = {"mismatch": len(mismatch),
                       "mismatch_tasks": sorted(mismatch),
                       "unverified": unverified, "current": current,
                       "total": len(mismatch) + unverified + current}
    return out


def turns_matrix() -> dict[str, list[str]]:
    from .util import read_json
    from . import assess
    thr = assess.load_cfg().get("pass_threshold", 0.8)
    out: dict[str, set] = {}
    if not config.RUNS_DIR.is_dir():
        return {}
    for mfile in config.RUNS_DIR.glob("*/*/*/metrics.json"):
        d = read_json(mfile, {})
        if d.get("status") != "max_turns":
            continue
        sc = read_json(mfile.parent / "score.json", {})
        score = sc.get("score")
        if sc.get("status") == "scored" and score is not None and score >= thr:
            continue
        out.setdefault(mfile.parents[1].name, set()).add(mfile.parent.name)
    return {m: sorted(t) for m, t in sorted(out.items())}


BUDGET_MUTE_TOKENS = 64
BUDGET_CEILING_FRAC = 0.9


def budget_matrix() -> dict[str, list[str]]:
    out: dict[str, set] = {}
    if not config.RUNS_DIR.is_dir():
        return {}
    caps = _model_caps()
    for mfile in config.RUNS_DIR.glob("*/*/*/metrics.json"):
        vis = _visible_answer(mfile, caps.get(mfile.parents[1].name))
        if vis is not None and vis <= BUDGET_MUTE_TOKENS:
            out.setdefault(mfile.parents[1].name, set()).add(mfile.parent.name)
    return {m: sorted(t) for m, t in sorted(out.items())}


def _model_caps() -> dict[str, int]:
    from .registry import load_models
    try:
        return {m.name: m.max_tokens for m in load_models(include_disabled=True)}
    except Exception:
        return {}


def _visible_answer(mfile, cap: int | None = None) -> int | None:
    from .util import read_json
    d = read_json(mfile, {})
    best = None
    for a in (d.get("attempts") or []):
        if a.get("error_kind") != "runaway":
            continue
        out, rz = a.get("tokens_out"), a.get("reasoning_tokens")
        if out is None or rz is None or out <= 0:
            continue
        if cap and out < cap * BUDGET_CEILING_FRAC:
            continue
        v = out - rz
        best = v if best is None else max(best, v)
    return best


def budget_reasons() -> dict[str, dict[str, str]]:
    from .util import read_json
    out: dict[str, dict[str, str]] = {}
    matrix = budget_matrix()
    if not matrix:
        return {}
    for mfile in config.RUNS_DIR.glob("*/*/*/metrics.json"):
        model, task = mfile.parents[1].name, mfile.parent.name
        if task not in matrix.get(model, []):
            continue
        vis = _visible_answer(mfile)
        if vis is None:
            continue
        d = read_json(mfile, {})
        cap = max((a.get("tokens_out") or 0) for a in (d.get("attempts") or []))
        out.setdefault(model, {})[task] = f"{vis} of {cap:,} tokens went to output"
    return out


class UsageLimitReached(Exception):
    def __init__(self, reset_at: float | None = None, reset_hint: str = ""):
        super().__init__("claude subscription usage limit reached")
        self.reset_at = reset_at
        self.reset_hint = reset_hint


class RequestRejected(Exception):

    def __init__(self, message: str, kind: str = "request_rejected") -> None:
        super().__init__(message)
        self.kind = kind


class RateLimited(Exception):
    def __init__(self, message: str = "", retry_after: float | None = None):
        super().__init__(message or "provider rate limit")
        self.detail = message
        self.retry_after = retry_after


RATE_LIMIT_STREAK = 3

SYSTEM_PROMPT = (
    "You are being evaluated by an automated benchmark harness. "
    "Solve the task exactly as instructed. Follow output format requirements precisely."
)

AGENT_SYSTEM_PROMPT = (
    "You are being evaluated by an automated benchmark harness. You have a private "
    "workspace directory and tools to list, read, write and run files in it. "
    "Work step by step: inspect the workspace, make your changes, and run your code "
    "to verify it before finishing. When everything works, reply with a short summary "
    "and no further tool calls."
)


def _cli_effort_default() -> str | None:
    from pathlib import Path as _P
    import json as _json
    import os as _os
    env = _os.environ.get("CLAUDE_EFFORT_LEVEL")
    if env:
        return env
    for cand in (config.ROOT / ".claude" / "settings.json",
                 _P.home() / ".claude" / "settings.json"):
        try:
            d = _json.loads(cand.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        lvl = d.get("effortLevel")
        if lvl:
            return str(lvl)
    return None


def new_run_id() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def new_run_ids(n: int, base: Path | None = None) -> list[str]:
    from datetime import timedelta
    base = base or config.RUNS_DIR
    out: list[str] = []
    t = datetime.now()
    while len(out) < max(1, n):
        rid = t.strftime("%Y-%m-%d_%H%M%S")
        if rid not in out and not (base / rid).exists():
            out.append(rid)
        t += timedelta(seconds=1)
    return out


def env_snapshot() -> dict:
    import platform
    import subprocess
    env = {"os": platform.platform(), "python": platform.python_version(),
           "host": platform.node()}
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
             "--format=csv,noheader"],
            capture_output=True, text=True, encoding="utf-8", timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            env["gpu"] = out.stdout.strip().splitlines()[0]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return env


class TaskRunner:
    def __init__(self, run_dir: Path, model: Model, adapter: BaseAdapter,
                 cancel=None):
        self.run_dir = run_dir
        self.model = model
        self.adapter = adapter
        self.cancel = cancel

    def _cancelled(self) -> bool:
        return self.cancel is not None and self.cancel.is_set()


    def _task_dir(self, task: Task) -> Path:
        d = self.run_dir / self.model.name / task.id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _log(self, task_dir: Path, event: str, data: dict) -> None:
        append_jsonl(task_dir / "transcript.jsonl", {"ts": now_iso(), "event": event, **data})

    def warm_up(self, preload_ms: float | None = None,
                unloaded_others: bool = False,
                model_info: dict | None = None) -> dict:
        t0 = now_ms()
        try:
            self.adapter.chat([{"role": "user", "content": "Reply with exactly: OK"}],
                              timeout_s=max(300, config.DEFAULT_REQUEST_TIMEOUT_S))
            err = None
        except AdapterError as e:
            err = str(e)
        ping_ms = round(now_ms() - t0, 1)
        meta = {"cold_start_ms": round(preload_ms, 1) if preload_ms else ping_ms,
                "preload_ms": round(preload_ms, 1) if preload_ms else None,
                "warm_ping_ms": ping_ms,
                "unloaded_others": unloaded_others,
                "warmup_error": err,
                "model_info": model_info,
                "local": self.model.local, "timestamp": now_iso()}
        write_json(self.run_dir / self.model.name / "model_meta.json", meta)
        return meta


    def _attempt(self, task_dir: Path, messages: list[dict], system: str,
                 tools: list[dict] | None, timeout_s: int, n: int) -> tuple[ChatResult | None, dict]:
        self._log(task_dir, "request", {
            "attempt": n, "n_messages": len(messages),
            "roles": [m["role"] for m in messages],
            "messages": messages[-1:]})
        rec: dict = {"n": n, "t_start": now_iso()}
        try:
            res = self.adapter.chat(messages, system=system, tools=tools, timeout_s=timeout_s)
        except AdapterError as e:
            rec.update({"error": str(e), "error_kind": e.kind,
                        "retryable": e.retryable, "reset_at": e.reset_at,
                        "reset_hint": e.reset_hint,
                        "retry_after": getattr(e, "retry_after", None),
                        "total_ms": None,
                        "ttft_ms": None, "tokens_in": None, "tokens_out": None})
            self._log(task_dir, "error", {"attempt": n, "kind": e.kind,
                                          "retryable": e.retryable,
                                          "message": str(e)})
            return None, rec
        rec.update({
            "error": None, "error_kind": None,
            "total_ms": round(res.total_ms, 1),
            "ttft_ms": round(res.ttft_ms, 1) if res.ttft_ms is not None else None,
            "first_text_ms": (round(res.first_text_ms, 1)
                              if res.first_text_ms is not None else None),
            "tokens_in": res.tokens_in, "tokens_out": res.tokens_out,
            "cache_read_tokens": res.cache_read_tokens,
            "cache_write_tokens": res.cache_write_tokens,
            "reasoning_tokens": res.reasoning_tokens,
            "stop_reason": res.stop_reason,
            "over_cap_tokens": res.over_cap_tokens,
            "cost_usd": res.cost_usd, "served_by": res.served_by,
        })
        self._log(task_dir, "response", {
            "attempt": n, "text": res.text, "stop_reason": res.stop_reason,
            "tokens_in": res.tokens_in, "tokens_out": res.tokens_out,
            "reasoning_tokens": res.reasoning_tokens,
            "total_ms": rec["total_ms"], "ttft_ms": rec["ttft_ms"],
            "cost_usd": res.cost_usd, "served_by": res.served_by,
            "tool_calls": [{"id": tc.id, "name": tc.name, "args": tc.args}
                           for tc in res.tool_calls],
        })
        return res, rec

    def _chat_with_retries(self, task_dir: Path, task: Task, messages: list[dict],
                           system: str, tools: list[dict] | None,
                           attempts: list[dict],
                           validate=None) -> ChatResult | None:
        runaway_retries = 0
        for n in range(1, task.max_retries + 2):
            if self._cancelled():
                return None
            res, rec = self._attempt(task_dir, messages, system, tools, task.timeout_s,
                                     len(attempts) + 1)
            attempts.append(rec)
            if res is None:
                if rec.get("error_kind") == "usage_limit":
                    raise UsageLimitReached(rec.get("reset_at"),
                                            rec.get("reset_hint", ""))
                if not rec.get("retryable"):
                    if rec.get("error_kind") in ("request_rejected", "auth",
                                                "infra"):
                        raise RequestRejected(str(rec.get("error") or "")[:300],
                                              rec.get("error_kind"))
                    return None
                if rec.get("error_kind") == "rate_limit":
                    wait = rec.get("retry_after") or min(10 * (2 ** (n - 1)), 60)
                    self._log(task_dir, "rate_limit",
                              {"attempt": n, "waiting_s": round(wait, 1)})
                    time.sleep(min(wait, 120))
                else:
                    time.sleep(min(2 ** n, 15))
                continue
            if validate:
                problem = validate(res)
                if problem:
                    runaway = res.stop_reason == "length"
                    rec["error"] = problem
                    rec["error_kind"] = "runaway" if runaway else "format"
                    self._log(task_dir, "format_error",
                              {"message": problem, "runaway": runaway})
                    if runaway:
                        runaway_retries += 1
                        if runaway_retries > 1:
                            return None
                    continue
            return res
        last = attempts[-1] if attempts else {}
        if last.get("error_kind") == "rate_limit":
            raise RateLimited(str(last.get("error") or "")[:200],
                              last.get("retry_after"))
        if last.get("error_kind") in ("request_rejected", "auth", "infra"):
            raise RequestRejected(str(last.get("error") or "")[:300],
                                  last.get("error_kind"))
        return None


    def run_task(self, task: Task) -> dict:
        self.adapter.task_category = task.category
        task_dir = self._task_dir(task)
        workspace = task_dir / "workspace"
        if workspace.exists():
            shutil.rmtree(workspace)
        workspace.mkdir(parents=True)
        if task.setup_dir:
            shutil.copytree(task.setup_dir, workspace, dirs_exist_ok=True)

        started = now_iso()
        t0 = now_ms()
        attempts: list[dict] = []
        turns = 0
        status = "ok"
        response_text = ""

        if task.tier >= 2 and self.model.provider == "claude-cli":
            turns, response_text, status = self._run_agentic_cli(task, task_dir,
                                                                 workspace, attempts)
        elif task.tier >= 2 and self.model.supports_tools:
            turns, response_text, status = self._run_agentic(task, task_dir, workspace, attempts)
        else:
            response_text, status = self._run_single(task, task_dir, workspace, attempts)
            turns = 1

        wall_ms = now_ms() - t0
        unreachable = never_reached_provider(attempts)
        if unreachable:
            score = {"status": "unscored", "score": None,
                     "summary": "never reached the provider — every attempt "
                                "failed before a request was sent, so nothing "
                                "was measured"}
            (task_dir / "score.json").unlink(missing_ok=True)
        else:
            score = self._score(task, workspace, response_text, status)
            write_json(task_dir / "score.json", score)

        tokens_in = _sum_tokens(attempts, "tokens_in")
        tokens_out = _sum_tokens(attempts, "tokens_out")
        reasoning_tokens = _sum_tokens(attempts, "reasoning_tokens")
        cache_read = _sum_tokens(attempts, "cache_read_tokens")
        cache_write = _sum_tokens(attempts, "cache_write_tokens")
        gen_ms = sum(a["total_ms"] - (a["ttft_ms"] or 0)
                     for a in attempts if a.get("total_ms"))
        per_attempt = [
            a.get("cost_usd") if a.get("cost_usd") is not None
            else self.model.cost_usd(a.get("tokens_in"), a.get("tokens_out"),
                                     a.get("cache_read_tokens"),
                                     a.get("cache_write_tokens"))
            for a in attempts]
        known = [c for c in per_attempt if c is not None]
        cost_usd = sum(known) if known \
            else self.model.cost_usd(tokens_in, tokens_out, cache_read, cache_write)
        cost_source = ("billed" if any(a.get("cost_usd") is not None
                                       for a in attempts) else "list")
        served_by = sorted({a["served_by"] for a in attempts
                            if a.get("served_by")})
        metrics = {
            "run_id": self.run_dir.name, "model": self.model.name,
            "task": task.id, "task_hash": task.content_hash,
            "category": task.category, "tier": task.tier,
            "started": started, "finished": now_iso(),
            "status": status,
            "failure_mode": _failure_mode(attempts, status),
            "wall_ms": round(wall_ms, 1),
            "turns": turns,
            "attempts": attempts,
            "n_attempts": len(attempts),
            "n_retries": max(0, len(attempts) - turns),
            "tokens_in": tokens_in, "tokens_out": tokens_out,
            "cache_read_tokens": cache_read, "cache_write_tokens": cache_write,
            "reasoning_tokens": reasoning_tokens,
            "sampling_used": self.model.sampling_payload(task.category),
            "sampling_profile": self.model.resolved_sampling(task.category)[1],
            "effort_used": (self.model.effort_as_tested
                            if self.model.effort_settable else None),
            "thinking_off": self.model.thinking_off or None,
            "cost_usd": cost_usd, "cost_source": cost_source,
            "served_by": served_by or None,
            "gen_tokens_per_sec": (round(tokens_out / (gen_ms / 1000), 2)
                                   if tokens_out and gen_ms > 0 else None),
            "prefill_tokens_per_sec": _prefill_tps(attempts),
        }
        write_json(task_dir / "metrics.json", metrics)
        return metrics

    def _run_single(self, task: Task, task_dir: Path, workspace: Path,
                    attempts: list[dict]) -> tuple[str, str]:
        prompt = task.prompt
        validate = None
        if task.scoring_type == "pytest":
            prompt += config.CODE_INSTRUCTION
            validate = lambda r: (None if scoring.extract_code_block(r.text)
                                  else "no python code block in response")
        elif task.scoring_type == "webapp":
            prompt += config.HTML_INSTRUCTION
            validate = lambda r: (None if scoring.extract_html_block(r.text)
                                  else "no html code block in response")
        elif task.scoring_type == "answer":
            prompt += config.ANSWER_INSTRUCTION
            validate = lambda r: (None if scoring.extract_answer(r.text)
                                  else "no ANSWER: line in response")
        elif task.scoring_type == "response":
            validate = lambda r: (None if (r.text or "").strip()
                                  else "empty response")

        res = self._chat_with_retries(task_dir, task, [{"role": "user", "content": prompt}],
                                      SYSTEM_PROMPT, None, attempts, validate)
        if res is None:
            return "", "error"
        if task.scoring_type == "pytest":
            code = scoring.extract_code_block(res.text)
            if code:
                (workspace / "solution.py").write_text(code, encoding="utf-8")
        elif task.scoring_type == "webapp":
            html_doc = scoring.extract_html_block(res.text)
            if html_doc:
                (workspace / "app.html").write_text(html_doc, encoding="utf-8")
        elif task.scoring_type == "response":
            (workspace / "response.txt").write_text(res.text, encoding="utf-8")
        return res.text, "ok"

    def _run_agentic_cli(self, task: Task, task_dir: Path, workspace: Path,
                         attempts: list[dict]) -> tuple[int, str, str]:
        from .adapters import AdapterError
        self._log(task_dir, "request", {
            "attempt": 1, "n_messages": 1, "roles": ["user"],
            "agent_harness": "claude-code-cli",
            "messages": [{"role": "user", "content": task.prompt}]})
        rec: dict = {"n": 1, "t_start": now_iso()}
        try:
            res = self.adapter.chat_agentic(task.prompt, workspace,
                                            task.max_turns, task.timeout_s)
        except AdapterError as e:
            rec.update({"error": str(e), "error_kind": e.kind, "total_ms": None,
                        "ttft_ms": None, "tokens_in": None, "tokens_out": None})
            attempts.append(rec)
            self._log(task_dir, "error", {"attempt": 1, "kind": e.kind,
                                          "message": str(e)})
            if e.kind == "usage_limit":
                raise UsageLimitReached(e.reset_at, e.reset_hint)
            return 0, "", "error"
        rec.update({"error": None, "error_kind": None,
                    "total_ms": round(res.total_ms, 1), "ttft_ms": None,
                    "tokens_in": res.tokens_in, "tokens_out": res.tokens_out,
                    "cache_read_tokens": res.cache_read_tokens,
                    "cache_write_tokens": res.cache_write_tokens,
                    "stop_reason": res.stop_reason,
                    "served_by": res.served_by})
        attempts.append(rec)
        self._log(task_dir, "response", {
            "attempt": 1, "text": res.text, "stop_reason": res.stop_reason,
            "tokens_in": res.tokens_in, "tokens_out": res.tokens_out,
            "total_ms": rec["total_ms"], "cli_turns": res.turns})
        return res.turns or 1, res.text, "ok"

    def _run_agentic(self, task: Task, task_dir: Path, workspace: Path,
                     attempts: list[dict]) -> tuple[int, str, str]:
        messages: list[dict] = [{"role": "user", "content": task.prompt}]
        turns = 0
        last_text = ""
        for _ in range(task.max_turns):
            if self._cancelled():
                return turns, last_text, "error"
            res = self._chat_with_retries(task_dir, task, messages,
                                          AGENT_SYSTEM_PROMPT, TOOL_DEFS, attempts)
            if res is None:
                return turns, last_text, "error"
            turns += 1
            last_text = res.text or last_text
            if not res.tool_calls:
                return turns, last_text, "ok"
            messages.append({"role": "assistant", "content": res.text,
                             "tool_calls": [{"id": tc.id, "name": tc.name, "args": tc.args}
                                            for tc in res.tool_calls]})
            results = []
            for tc in res.tool_calls:
                output = execute_tool(workspace, tc.name, tc.args)
                self._log(task_dir, "tool_result",
                          {"tool": tc.name, "args": tc.args, "output": output})
                results.append({"id": tc.id, "name": tc.name, "output": output})
            messages.append({"role": "tool_results", "results": results})
        return turns, last_text, "max_turns"

    def _score(self, task: Task, workspace: Path, response_text: str, status: str) -> dict:
        if status == "error":
            return {"status": "scored", "score": 0.0, "scored_by": "harness",
                    "summary": "run failed (all attempts errored)", "timestamp": now_iso()}
        st = task.scoring_type
        if st in ("pytest", "webapp", "response"):
            return scoring.run_pytest_checker(task, workspace)
        if st == "answer":
            return scoring.score_answer(task, response_text)
        return scoring.pending_manual()


def _prefill_tps(attempts: list[dict]) -> float | None:
    pre = [a for a in attempts if a.get("ttft_ms") and a.get("tokens_in")]
    if not pre:
        return None
    return round(sum(a["tokens_in"] for a in pre)
                 / (sum(a["ttft_ms"] for a in pre) / 1000), 1)


NEVER_REACHED_KINDS = ("connect",)


def never_reached_provider(attempts: list[dict]) -> bool:
    if not attempts:
        return False
    errs = [a for a in attempts if a.get("error")]
    if len(errs) != len(attempts):
        return False
    if any(a.get("tokens_in") or a.get("tokens_out") for a in attempts):
        return False
    return all(a.get("error_kind") in NEVER_REACHED_KINDS for a in errs)


def _sum_tokens(attempts: list[dict], key: str) -> int | None:
    vals = [a[key] for a in attempts if a.get(key) is not None]
    return sum(vals) if vals else None


def _failure_mode(attempts: list[dict], status: str) -> str | None:
    if status == "max_turns":
        return "max_turns"
    if not attempts:
        return None
    last = attempts[-1]
    if last.get("error_kind") == "repetition_loop":
        return "repetition_loop"
    if last.get("error_kind") == "runaway":
        return "runaway"
    if last.get("error_kind") == "timeout":
        return "timeout"
    if last.get("error_kind"):
        return "error"
    return None


_CTX_CHUNK = 16384


def _ctx_bucket(need: int) -> int:
    import math
    return max(_CTX_CHUNK, math.ceil(need / _CTX_CHUNK) * _CTX_CHUNK)


def context_buckets(model: Model, tasks: list[Task]) -> list[tuple]:
    cap = model.context_length or 0
    groups: dict[int, list] = {}
    for t in tasks:
        need = len(t.prompt) // 3 + model.max_tokens + 1024
        ctx = _ctx_bucket(max(need, 4096))
        if cap:
            ctx = min(ctx, cap)
        groups.setdefault(ctx, []).append(t)
    return [(c, sorted(groups[c], key=lambda t: t.id)) for c in sorted(groups)]


_VRAM_MB_CACHE = "unset"


def _gpu_vram_mb():
    global _VRAM_MB_CACHE
    if _VRAM_MB_CACHE != "unset":
        return _VRAM_MB_CACHE
    import subprocess
    val = None
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            val = int(r.stdout.strip().splitlines()[0].strip())
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        val = None
    _VRAM_MB_CACHE = val
    return val


def _bucket_offload(fp: dict | None, ctx: int, vram_mb) -> str:
    if not fp or not vram_mb:
        return "auto"
    need_gb = fp["weights_gb"] + fp["kv_fixed_gb"] + fp["kv_per_tok_gb"] * ctx
    safe_gb = (vram_mb / 1024.0) * 0.90
    return "max" if need_gb <= safe_gb else "auto"


def load_plan(model: Model, tasks: list[Task], footprint=None, vram_mb=None) -> list[tuple]:
    buckets = context_buckets(model, tasks)
    max_tasks, max_ctx, groups = [], 0, []
    for ctx, g in buckets:
        if _bucket_offload(footprint, ctx, vram_mb) == "max":
            max_tasks += g
            max_ctx = max(max_ctx, ctx)
        else:
            groups.append((ctx, "auto", g))
    if max_tasks:
        groups.append((max_ctx, "max", sorted(max_tasks, key=lambda t: t.id)))
    groups.sort(key=lambda x: x[0])
    return groups


def _stamp_load_plan(meta_path, plan: list[tuple]) -> None:
    from .util import read_json
    meta = read_json(meta_path, {})
    if not meta:
        return
    meta["load_strategy"] = ("grouped-context" if len(plan) > 1
                             else "single-context")
    meta["context_groups"] = [{"ctx": c, "gpu": off, "n_tasks": len(g)}
                              for c, off, g in plan]
    write_json(meta_path, meta)


def run_model(run_dir: Path, model: Model, tasks: list[Task], progress=print,
              manage_memory: bool = True, cancel=None, spend=None) -> None:
    run_model_cycles([run_dir], model, tasks, progress, manage_memory, cancel,
                     spend=spend)


def _stop_all(run_dirs, model_name: str, reason: str,
              extra: dict | None = None) -> None:
    from .util import read_json
    for rd in run_dirs:
        mani_path = rd / "run.json"
        mani = read_json(mani_path, {})
        if not mani:
            continue
        mani["stopped_reason"] = reason
        for k, v in (extra or {}).items():
            mani[k] = v
        mani.setdefault("stopped_models", [])
        if model_name not in mani["stopped_models"]:
            mani["stopped_models"].append(model_name)
        write_json(mani_path, mani)


def run_model_cycles(run_dirs: list[Path], model: Model, tasks: list[Task],
                     progress=print, manage_memory: bool = True,
                     cancel=None, spend=None) -> None:
    from .util import read_json
    adapter = make_adapter(model)
    runners = [TaskRunner(rd, model, adapter, cancel=cancel) for rd in run_dirs]
    n_cycles = len(runners)
    progress(f"[{model.name}] start ({model.provider}"
             f"{', local' if model.local else ''}"
             f"{f', {n_cycles} cycles per load' if n_cycles > 1 else ''})")
    sampler = None
    if model.local:
        from .telemetry import GpuSampler
        if GpuSampler.available():
            sampler = GpuSampler()
            sampler.start()
    try:
        if not model.local and "openrouter" in (model.base_url or ""):
            from .interfaces import endpoint_quants
            quants = endpoint_quants(model.model)
            if quants:
                for rd in run_dirs:
                    write_json(rd / model.name / "model_meta.json", {
                        "local": False, "gateway_quants": quants,
                        "timestamp": now_iso()})
        lms = None
        lms_ctl = False
        if model.local:
            from . import lmstudio as lms
            lms_ctl = bool(lms.lms_exe())
        _fp = gguf.footprint(model.model) if lms_ctl else None
        _vram = _gpu_vram_mb() if lms_ctl else None
        plan = (load_plan(model, tasks, _fp, _vram) if lms_ctl
                else [(0, "auto", list(tasks))])

        def _skipped(t: Task) -> bool:
            return (t.tier >= 2 and not model.supports_tools
                    and model.provider != "claude-cli")

        def _spread(meta: dict) -> None:
            for rd in run_dirs[1:]:
                write_json(rd / model.name / "model_meta.json", meta)

        if model.local and not lms_ctl:
            progress(f"[{model.name}] warm-up ping (JIT — no lms context control)...")
            meta = runners[0].warm_up(model_info=None)
            _spread(meta)
            if meta["warmup_error"]:
                progress(f"[{model.name}] !! warm-up failed: {meta['warmup_error']}"
                         " — skipping model")
                return

        loaded_ctx = None
        rl_streak = 0
        for bctx, gpu, group in plan:
            for t in group:
                if _skipped(t):
                    progress(f"[{model.name}] {t.id}: skipped "
                             f"(supports_tools: false)")
            live = [t for t in group if not _skipped(t)]
            if not live:
                continue
            if lms_ctl and bctx != loaded_ctx:
                unloaded = False
                if manage_memory:
                    progress(f"[{model.name}] lms: unloading to free VRAM...")
                    unloaded = lms.unload_all(
                        progress=lambda m: progress(f"[{model.name}] {m}"))
                progress(f"[{model.name}] lms: loading {model.model} @ context "
                         f"{bctx:,} ({gpu} GPU offload) for {len(live)} task(s)"
                         f"{f' x {n_cycles} cycles' if n_cycles > 1 else ''}...")
                preload_ms = lms.load_model(
                    model.model, progress=lambda m: progress(f"[{model.name}] {m}"),
                    context_length=bctx, gpu_offload=gpu)
                info = lms.model_info(model.base_url or "http://localhost:1234/v1",
                                      model.key_env, model.model)
                meta = runners[0].warm_up(preload_ms=preload_ms,
                                          unloaded_others=unloaded, model_info=info)
                _spread(meta)
                if meta["warmup_error"]:
                    progress(f"[{model.name}] !! warm-up failed: "
                             f"{meta['warmup_error']} — skipping model")
                    return
                for rd in run_dirs:
                    _stamp_load_plan(rd / model.name / "model_meta.json", plan)
                progress(f"[{model.name}] loaded @ {bctx:,} "
                         f"(cold {meta['cold_start_ms'] / 1000:.1f}s)")
                loaded_ctx = bctx
            for cycle in range(n_cycles):
                runner = runners[cycle]
                run_dir = runner.run_dir
                if n_cycles > 1:
                    progress(f"[{model.name}] cycle {cycle + 1}/{n_cycles} @ "
                             f"context {bctx:,} ({len(live)} task(s)) "
                             f"-> {run_dir.name}")
                for task in live:
                    if cancel is not None and cancel.is_set():
                        progress(f"[{model.name}] stopped by user — remaining "
                                 f"tasks skipped")
                        return
                    try:
                        m = runner.run_task(task)
                        rl_streak = 0
                        if spend is not None:
                            spend.add(m.get("cost_usd"))
                    except RequestRejected as rr:
                        task_dir = run_dir / model.name / task.id
                        if task_dir.exists():
                            shutil.rmtree(task_dir, ignore_errors=True)
                        _record_dropped(run_dir, model.name, task.id, rr.kind)
                        done = sum(1 for t in tasks
                                   if (run_dir / model.name / t.id / "score.json").exists())
                        progress(
                            f"[{model.name}] {task.id}: provider REFUSED the request "
                            f"({rr.kind}) - dropped UNSCORED, not zeroed. Every "
                            f"remaining task would be refused the same way, so this "
                            f"model is skipped. {done} completed task(s) saved. Fix the "
                            f"model's config and re-run {model.name}. -- {rr}")
                        _stop_all(run_dirs, model.name, rr.kind)
                        return
                    except RateLimited as rl:
                        task_dir = run_dir / model.name / task.id
                        if task_dir.exists():
                            shutil.rmtree(task_dir, ignore_errors=True)
                        _record_dropped(run_dir, model.name, task.id, "rate_limit")
                        rl_streak += 1
                        progress(f"[{model.name}] {task.id}: provider rate-limited "
                                 f"(429) - dropped UNSCORED, not zeroed. Re-run to fill "
                                 f"it in.")
                        if rl_streak < RATE_LIMIT_STREAK:
                            continue
                        done = sum(1 for t in tasks
                                   if (run_dir / model.name / t.id / "score.json").exists())
                        progress(
                            f"[{model.name}] rate-limited on {rl_streak} tasks in a row "
                            f"- skipping this model's remaining tasks. {done} completed "
                            f"task(s) saved, nothing scored as failure. Add your own "
                            f"provider key or retry later, then re-run "
                            f"{model.name} to fill the gaps.")
                        _stop_all(run_dirs, model.name, "rate_limit")
                        return
                    except UsageLimitReached as ul:
                        task_dir = run_dir / model.name / task.id
                        if task_dir.exists():
                            shutil.rmtree(task_dir, ignore_errors=True)
                        _record_dropped(run_dir, model.name, task.id, "usage_limit")
                        when = ul.reset_hint or (f"resets {_fmt_epoch(ul.reset_at)}"
                                                 if ul.reset_at else "")
                        done = sum(1 for t in tasks
                                   if (run_dir / model.name / t.id / "score.json").exists())
                        progress(
                            f"[{model.name}] {task.id}: Claude usage limit reached"
                            f"{f' — {when}' if when else ''}. Dropped this task; "
                            f"{done} completed task(s) saved. Skipping {model.name}'s "
                            f"remaining tasks — re-run after the reset to continue "
                            f"(finished tasks won't repeat).")
                        _stop_all(run_dirs, model.name, "usage_limit",
                                  {"reset_at": ul.reset_at,
                                   "reset_hint": ul.reset_hint})
                        return
                    except Exception as e:
                        progress(f"[{model.name}] !! {task.id} crashed the runner: "
                                 f"{type(e).__name__}: {e} — recorded as error, "
                                 "continuing with the next task")
                        task_dir = run_dir / model.name / task.id
                        task_dir.mkdir(parents=True, exist_ok=True)
                        m = {"run_id": run_dir.name, "model": model.name,
                             "task": task.id, "task_hash": task.content_hash,
                             "category": task.category, "tier": task.tier,
                             "started": now_iso(), "finished": now_iso(),
                             "status": "error", "wall_ms": 0, "turns": 0,
                             "attempts": [], "n_attempts": 0, "n_retries": 0,
                             "tokens_in": None, "tokens_out": None, "cost_usd": None,
                             "gen_tokens_per_sec": None,
                             "prefill_tokens_per_sec": None,
                             "crash": f"{type(e).__name__}: {e}"}
                        write_json(task_dir / "metrics.json", m)
                        write_json(task_dir / "score.json", {
                            "status": "scored", "score": 0.0, "scored_by": "harness",
                            "summary": f"harness exception: {type(e).__name__}: {e}",
                            "timestamp": now_iso()})
                    s = read_json(run_dir / model.name / task.id / "score.json", {})
                    score_str = ("pending review" if s.get("status") == "pending"
                                 else f"score {s.get('score', 0):.2f}")
                    progress(f"[{model.name}] {task.id}: {m['status']}, {score_str}, "
                             f"{m['wall_ms'] / 1000:.1f}s, "
                             f"tok {m['tokens_in'] or '?'}/{m['tokens_out'] or '?'}, "
                             f"retries {m['n_retries']}")
        progress(f"[{model.name}] done")
    finally:
        if sampler:
            gpu = sampler.stop()
            if gpu:
                for rd in run_dirs:
                    meta_path = rd / model.name / "model_meta.json"
                    meta = read_json(meta_path, {})
                    meta["gpu"] = gpu
                    write_json(meta_path, meta)
                progress(f"[{model.name}] gpu: peak {gpu['vram_peak_mb']:,} MB "
                         f"VRAM · avg {gpu['power_avg_w']:.0f} W · "
                         f"{gpu['energy_wh']:.2f} Wh")
        if model.local and manage_memory:
            try:
                from . import lmstudio as _lms
                if _lms.lms_exe():
                    _lms.unload_all(progress=lambda m: progress(f"[{model.name}] {m}"))
                    progress(f"[{model.name}] lms: unloaded (VRAM freed)")
            except Exception:
                pass


def _record_dropped(run_dir: Path, model: str, task: str, reason: str) -> None:
    from .util import read_json, write_json
    try:
        mani_path = run_dir / "run.json"
        mani = read_json(mani_path, {})
        lst = mani.setdefault("dropped_unscored", [])
        entry = {"model": model, "task": task, "reason": reason}
        if entry not in lst:
            lst.append(entry)
        write_json(mani_path, mani)
    except OSError:
        pass


def _persisting_progress(run_dirs, progress, lock=None):
    import threading
    lock = lock or threading.Lock()
    if isinstance(run_dirs, Path):
        run_dirs = [run_dirs]
    log_paths = [rd / "run.log" for rd in run_dirs]

    def wrapped(line):
        stamped = f"{now_iso()} {line}\n"
        for log_path in log_paths:
            try:
                with lock, open(log_path, "a", encoding="utf-8") as fh:
                    fh.write(stamped)
            except OSError:
                pass
        progress(line)

    return wrapped


def run_suite(models: list[Model], tasks: list[Task], run_dir: Path | None = None,
              tag: str = "", progress=print, parallel: bool = False,
              cancel=None, force: bool = False,
              run_dirs: list[Path] | None = None) -> Path:
    import threading

    from .validate import validate_models
    problems = validate_models(models)
    if problems:
        raise ValueError("model configuration problems — fix these before "
                         "running:\n  " + "\n  ".join(problems))

    from . import budget
    pre = budget.preflight(models, tasks, len(run_dirs) if run_dirs else 1)
    if pre["problems"] and not force:
        raise SpendRefused(
            "refusing to start on cost grounds:\n  "
            + "\n  ".join(pre["problems"])
            + f"\nestimated billable spend ${pre['estimate']['billable']:,.2f}."
            + (" Raise max_spend_usd in settings.local.json, top up the"
               " provider, or pass --force." if pre["cap"] is not None else
               " Top up the provider, or pass --force."))
    _spend = budget.SpendTracker(pre["cap"])

    busy = None if force else active_run()
    if busy:
        raise RunInProgress(
            f"run {busy} is already executing. A second concurrent run competes "
            "for the same CPU and GPU that its timing-sensitive measurements "
            "depend on, and would corrupt both. Wait for it, stop it, or delete "
            "it if it crashed. (--force overrides.)")

    if not run_dirs:
        run_dirs = [run_dir or (config.RUNS_DIR / new_run_id())]
    run_dir = run_dirs[0]
    n_cycles = len(run_dirs)
    manifests = []
    for i, rd in enumerate(run_dirs):
        rd.mkdir(parents=True, exist_ok=True)
        manifests.append(_manifest(models, tasks, rd, tag, parallel, i, n_cycles,
                                   run_dirs[0].name,
                                   _forecast_record(pre, n_cycles)))
        write_json(rd / "run.json", manifests[i])

    from .util import keep_awake, read_json
    log = _persisting_progress(run_dirs, progress)
    if pre["estimate"]["billable"]:
        log(f"estimated billable spend: "
            f"${pre['estimate']['billable']:,.2f}"
            + (f" (ceiling ${pre['cap']:,.2f})" if pre["cap"] else
               " (no ceiling set; put max_spend_usd in settings.local.json)"))
    for _n, _b in (pre["balances"] or {}).items():
        if _b and _b.get("remaining") is not None:
            log(f"{_b['provider']}: ${_b['remaining']:,.2f} available")
    try:
        with keep_awake():
            _run_all(models, tasks, run_dirs, log, parallel, cancel,
                     spend=_spend)
    except budget.SpendExceeded as e:
        log(f"!! {e}")
        for rd in run_dirs:
            _stop_all([rd], "*", "spend_ceiling")

    for rd, manifest in zip(run_dirs, manifests):
        disk = read_json(rd / "run.json", {})
        for k in ("stopped_reason", "reset_at", "reset_hint", "stopped_models",
                  "dropped_unscored"):
            if k in disk:
                manifest[k] = disk[k]
        manifest["finished"] = now_iso()
        write_json(rd / "run.json", manifest)
    return run_dir


def _forecast_record(pre: dict, n_cycles: int) -> dict:
    est = pre.get("estimate") or {}
    rows = []
    for r in est.get("rows") or []:
        if r.get("local") or r.get("subscription"):
            continue
        rows.append({k: r[k] for k in
                     ("model", "basis", "priced", "tasks", "missing",
                      "modelled", "blind", "known", "projected", "total")
                     if k in r})
    bal = {}
    for b in (pre.get("balances") or {}).values():
        if b and b.get("remaining") is not None:
            bal[b["provider"]] = b["remaining"]
    return {
        "at": now_iso(),
        "billable": est.get("billable"),
        "known": est.get("known"),
        "projected": est.get("projected"),
        "unpriced_cells": est.get("unpriced_cells"),
        "repeat": est.get("repeat"),
        "cycles": n_cycles,
        "cap": pre.get("cap"),
        "problems": pre.get("problems") or [],
        "balance_at_start": bal,
        "models": rows,
    }


def _manifest(models, tasks, run_dir: Path, tag: str, parallel: bool,
              index: int, n_cycles: int, group: str,
              forecast: dict | None = None) -> dict:
    manifest = {
        "run_id": run_dir.name, "tag": tag, "started": now_iso(),
        "suite_version": config.suite_version(),
        "env": env_snapshot(),
        "mode": "parallel" if parallel else "serial",
        "models": [m.name for m in models],
        "model_sampling": {
            m.name: {"max_tokens": m.max_tokens, "temperature": m.temperature,
                     "sampling": dict(m.sampling or {}),
                     "sampling_profiles": {k: dict(v) for k, v in
                                           (m.sampling_profiles or {}).items()},
                     "effort": (m.effort_as_tested if m.effort_settable
                                else None)}
            for m in models},
        "cli_effort_default": _cli_effort_default(),
        "tasks": [{"id": t.id, "hash": t.content_hash, "tier": t.tier,
                   "category": t.category} for t in tasks],
        "cost_forecast": forecast,
        "finished": None,
    }
    if n_cycles > 1:
        manifest["cycle"] = index + 1
        manifest["cycles"] = n_cycles
        manifest["cycle_group"] = group
    return manifest


def cycling_models(models: list[Model], repeat: int) -> list[Model]:
    if repeat < 2:
        return []
    from . import lmstudio as lms
    if not lms.lms_exe():
        return []
    return [m for m in models if m.local]


def cycles_for(model: Model, run_dirs: list[Path]) -> list[Path]:
    return (run_dirs if cycling_models([model], len(run_dirs))
            else run_dirs[:1])


def cycle_plan_summary(models: list[Model], tasks: list[Task],
                       repeat: int) -> list[str]:
    cycling = cycling_models(models, repeat)
    if not cycling:
        return []
    vram = _gpu_vram_mb()
    lines = []
    for m in cycling:
        plan = load_plan(m, tasks, gguf.footprint(m.model), vram)
        detail = " + ".join(f"{c:,} {o} ({len(g)} task"
                            f"{'' if len(g) == 1 else 's'})"
                            for c, o, g in plan)
        lines.append(
            f"{m.name}: {len(plan)} model load(s), each running all {repeat} "
            f"cycles — was {len(plan) * repeat} loads. {detail}")
    return lines


def _run_all(models, tasks, run_dirs, progress, parallel, cancel,
             spend=None) -> None:
    run_dir = run_dirs[0]
    if parallel and len(models) > 1:
        threads = [threading.Thread(target=run_model,
                                    args=(run_dir, m, tasks, progress, False, cancel),
                                    daemon=True) for m in models]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    else:
        for model in models:
            if cancel is not None and cancel.is_set():
                break
            mine = cycles_for(model, run_dirs)
            if len(mine) > 1:
                run_model_cycles(mine, model, tasks, progress, cancel=cancel,
                                 spend=spend)
            else:
                for rd in run_dirs:
                    if cancel is not None and cancel.is_set():
                        break
                    run_model(rd, model, tasks, progress, cancel=cancel,
                              spend=spend)
