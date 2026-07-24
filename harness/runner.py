"""The run engine. Sequential by design: local models share one GPU, so
parallel requests would corrupt timing. Every request/response is written
verbatim to transcript.jsonl; metrics.json aggregates timing/tokens/cost.

Run layout:
    runs/<run-id>/run.json                          — run manifest
    runs/<run-id>/<model>/model_meta.json           — warm-up / cold-start info
    runs/<run-id>/<model>/<task>/transcript.jsonl
    runs/<run-id>/<model>/<task>/metrics.json
    runs/<run-id>/<model>/<task>/score.json
    runs/<run-id>/<model>/<task>/workspace/         — the model's sandbox
"""

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
    """Another run is already executing — starting a second would corrupt both."""


def active_run() -> str | None:
    """The run currently executing, from DISK — not from in-process state.

    The job manager's one-at-a-time lock lives in memory, so it only guards its
    own process; a second server or CLI `harness run` sees "idle" and starts a
    concurrent run (CPU contention then corrupts the timing budgets — v0.5.9).
    runs/ is the one thing every process shares, so it is the honest lock.
    """
    from .util import read_json
    for base in (config.RUNS_DIR, getattr(config, "SCOUTS_DIR", None),
                 getattr(config, "SPECIAL_DIR", None)):
        if not base or not base.is_dir():
            continue
        for run_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            manifest = read_json(run_dir / "run.json", {})
            if manifest and not manifest.get("finished"):
                return run_dir.name
    return None


def _window_limited() -> dict[str, dict[str, str]]:
    """{model: {task: reason}} for the cells a bigger WINDOW might rescue, across
    the live runs/. Both qualifying modes are time-bound — the model just needed
    more wall-clock:

      * "silence" — legacy rumination_spiral: the claude CLI thought with no
                    output until the (now retired) no-output guard killed it.
                    Silence was never a spiral, only a too-tight window.
      * "timeout" — hit the wall-clock deadline unrecovered (status stayed error
                    through the last attempt); this is also where claude silence
                    lands now that the guard is gone.

    A runaway (token ceiling) and a repetition_loop (a real spiral, going in
    circles) are both EXCLUDED: neither is fixed by more time."""
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
    """{model: [task ids]} a wider window might rescue — rumination spirals plus
    unrecovered timeouts. Feeds the Special window probe (which raises each
    task's own timeout to the window, so both modes get the extra time). See
    _window_limited for why runaways are excluded."""
    return {m: sorted(t) for m, t in sorted(_window_limited().items())}


def window_reasons() -> dict[str, dict[str, str]]:
    """Per-cell reason ('spiral' | 'timeout') behind spiral_matrix(), so the
    special page can label why each cell is in the probe set."""
    return _window_limited()


def turns_matrix() -> dict[str, list[str]]:
    """{model: [agentic task ids]} where the model FAILED by exhausting the turn
    budget — status=="max_turns" AND it did not reach a passing score. Feeds the
    Special turn-budget probe, which re-runs these with a raised max_turns to see
    whether more steps let the model converge.

    A max_turns run that still PASSED (finished the work, just never emitted a
    clean stop before the cap) is excluded — the cap didn't cost it anything. A
    partial score IS included: extra turns might carry it the rest of the way.
    This is the turn-count analog of _window_limited (time); the two are separate
    because more time and more turns are different remedies."""
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


class UsageLimitReached(Exception):
    """A Claude subscription cap was hit. Unwinds the current task without
    scoring it (a re-run after the reset fills it in) and pauses the run."""
    def __init__(self, reset_at: float | None = None, reset_hint: str = ""):
        super().__init__("claude subscription usage limit reached")
        self.reset_at = reset_at
        self.reset_hint = reset_hint


class RateLimited(Exception):
    """The provider rate-limited us and the task never got to run.

    Same reasoning as UsageLimitReached, different cause: this is OUR access
    being throttled, not the model failing. Scoring it 0.0 would put a
    capability failure on a model that never got a turn - kimi-k3 scored 1.0 on
    every task it reached while landing 0.25 raw, purely because its provider
    was busy. So the task is dropped unscored and a re-run fills it in.
    """
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


def new_run_id() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def env_snapshot() -> dict:
    """Hardware/software fingerprint stored in every run manifest — cross-date
    speed comparisons are only meaningful on a known-identical rig."""
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
        """One throwaway ping so a JIT-loaded local model doesn't pollute the
        first timed task. When pre-loaded via lms, load time arrives as
        preload_ms and the ping is just a warm check."""
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
        """One request. Returns (result_or_None, attempt_record)."""
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
        """Retry loop. `validate(res) -> str|None` returns an error string for
        format failures (which also consume an attempt — the clock never lies)."""
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
        return None


    def run_task(self, task: Task) -> dict:
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
        """Tier-2 via Claude Code's own tools; one `claude -p` invocation
        (cwd = workspace) is the whole episode."""
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


def _sum_tokens(attempts: list[dict], key: str) -> int | None:
    vals = [a[key] for a in attempts if a.get(key) is not None]
    return sum(vals) if vals else None


def _failure_mode(attempts: list[dict], status: str) -> str | None:
    """Coarse label for why a task ended badly, for reporting. None when the
    final attempt succeeded (a task that ran away once then recovered is not
    tagged)."""
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
    """Round a needed context up to the next 16k chunk. Fine enough that a 64k
    task doesn't get loaded in a 128k window (which would needlessly spill), yet
    coarse enough that the many ~34k short tasks share one load."""
    import math
    return max(_CTX_CHUNK, math.ceil(need / _CTX_CHUNK) * _CTX_CHUNK)


def context_buckets(model: Model, tasks: list[Task]) -> list[tuple]:
    """Group tasks by the context window they need, ascending. A local run then
    loads the model once per group at the smallest window that serves it, so
    short-context tasks stay resident in VRAM and run at full speed while only
    the genuinely large-context tasks pay the big-window (and, past the card, the
    shared-memory-spill) cost. Returns [(ctx, [tasks]), ...] ascending; the yaml
    context_length caps every bucket. Deterministic (sorted) for repeatability."""
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
    """Total GPU VRAM in MiB via nvidia-smi (a leaf query), or None when there's
    no NVIDIA GPU / nvidia-smi. Cached for the process."""
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
    """'max' when the model + this context's KV comfortably fit VRAM — force
    every layer onto the GPU (fast). 'auto' when it would overflow, so LM Studio
    parks the excess on the CPU (slow, ~8 tok/s, but it COMPLETES) instead of
    '--gpu max' forcing a shared-memory spill to ~0.03 tok/s that hangs the whole
    machine. 'auto' too when we can't measure — the safe default never spills."""
    if not fp or not vram_mb:
        return "auto"
    need_gb = fp["weights_gb"] + fp["kv_fixed_gb"] + fp["kv_per_tok_gb"] * ctx
    safe_gb = (vram_mb / 1024.0) * 0.90
    return "max" if need_gb <= safe_gb else "auto"


def load_plan(model: Model, tasks: list[Task], footprint=None, vram_mb=None) -> list[tuple]:
    """Ordered [(ctx, gpu_offload, [tasks])] for a local run.

    Starts from context_buckets, then COALESCES every bucket that fits VRAM
    ('max') into a single load at the largest fitting context — so a small model
    that fits even its biggest context loads ONCE, not once per bucket (e4b was
    reloading 5x for nothing). Buckets that overflow stay separate ('auto'), each
    at its own context, so an oversized task isn't loaded at a needlessly larger
    window (which would offload more to the CPU and run slower). Ascending by
    load context; the coalesced 'max' group (if any) is the small-context one."""
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
    """Record the context-bucket load plan on model_meta.json so every run is
    self-describing — speed numbers (tok/s, wall) are only comparable within the
    same plan. Merges into whatever warm_up just wrote."""
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
              manage_memory: bool = True, cancel=None) -> None:
    """Run every task against one model. Safe to call from a thread — each
    model writes only inside its own run_dir/<model>/ subtree."""
    from .util import read_json
    adapter = make_adapter(model)
    runner = TaskRunner(run_dir, model, adapter, cancel=cancel)
    progress(f"[{model.name}] start ({model.provider}"
             f"{', local' if model.local else ''})")
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
                write_json(run_dir / model.name / "model_meta.json", {
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
        ordered = [t for _c, _o, g in plan for t in g]
        task_ctx = {t.id: c for c, _o, g in plan for t in g}
        task_gpu = {t.id: o for c, o, g in plan for t in g}

        if model.local and not lms_ctl:
            progress(f"[{model.name}] warm-up ping (JIT — no lms context control)...")
            meta = runner.warm_up(model_info=None)
            if meta["warmup_error"]:
                progress(f"[{model.name}] !! warm-up failed: {meta['warmup_error']}"
                         " — skipping model")
                return

        loaded_ctx = None
        rl_streak = 0
        for task in ordered:
            if cancel is not None and cancel.is_set():
                progress(f"[{model.name}] stopped by user — remaining tasks skipped")
                return
            skip = (task.tier >= 2 and not model.supports_tools
                    and model.provider != "claude-cli")
            if lms_ctl and not skip and task_ctx[task.id] != loaded_ctx:
                bctx = task_ctx[task.id]
                unloaded = False
                if manage_memory:
                    progress(f"[{model.name}] lms: unloading to free VRAM...")
                    unloaded = lms.unload_all(
                        progress=lambda m: progress(f"[{model.name}] {m}"))
                n_here = sum(1 for t in ordered if task_ctx[t.id] == bctx and not
                             (t.tier >= 2 and not model.supports_tools
                              and model.provider != "claude-cli"))
                gpu = task_gpu[task.id]
                progress(f"[{model.name}] lms: loading {model.model} @ context "
                         f"{bctx:,} ({gpu} GPU offload) for {n_here} task(s)...")
                preload_ms = lms.load_model(
                    model.model, progress=lambda m: progress(f"[{model.name}] {m}"),
                    context_length=bctx, gpu_offload=gpu)
                info = lms.model_info(model.base_url or "http://localhost:1234/v1",
                                      model.key_env, model.model)
                meta = runner.warm_up(preload_ms=preload_ms, unloaded_others=unloaded,
                                      model_info=info)
                if meta["warmup_error"]:
                    progress(f"[{model.name}] !! warm-up failed: "
                             f"{meta['warmup_error']} — skipping model")
                    return
                _stamp_load_plan(runner.run_dir / model.name / "model_meta.json",
                                 plan)
                progress(f"[{model.name}] loaded @ {bctx:,} "
                         f"(cold {meta['cold_start_ms'] / 1000:.1f}s)")
                loaded_ctx = bctx
            if skip:
                progress(f"[{model.name}] {task.id}: skipped (supports_tools: false)")
                continue
            try:
                m = runner.run_task(task)
                rl_streak = 0
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
                mani_path = run_dir / "run.json"
                mani = read_json(mani_path, {})
                mani["stopped_reason"] = "rate_limit"
                mani.setdefault("stopped_models", [])
                if model.name not in mani["stopped_models"]:
                    mani["stopped_models"].append(model.name)
                write_json(mani_path, mani)
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
                mani_path = run_dir / "run.json"
                mani = read_json(mani_path, {})
                mani["stopped_reason"] = "usage_limit"
                mani["reset_at"] = ul.reset_at
                mani["reset_hint"] = ul.reset_hint
                mani.setdefault("stopped_models", [])
                if model.name not in mani["stopped_models"]:
                    mani["stopped_models"].append(model.name)
                write_json(mani_path, mani)
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
                meta_path = run_dir / model.name / "model_meta.json"
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
    """Append (model, task, reason) to the manifest's dropped_unscored list.

    A task dropped WITHOUT a score — rate-limited (429) below the streak
    threshold, or usage-capped — otherwise leaves a SILENT coverage gap: no
    dir, no result row, and (below the streak) no stopped_models entry either,
    so the cell just reads "not run" with no explanation. This makes the drop
    queryable from run.json. Best-effort — a logging failure must not abort the
    run. (Matches the existing unlocked read-modify-write of run.json; serial is
    the default and only mode where the manifest is contended.)"""
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


def _persisting_progress(run_dir: Path, progress, lock=None):
    """Wrap a progress callback so every narration line is ALSO appended to
    run_dir/run.log (timestamped), then forwarded to the original sink.

    The output window only ever held the last ~200 lines in memory and nothing
    reached disk, so a model that got skipped, rate-limited, usage-capped or
    crashed left no record of WHY — the reason had to be reverse-engineered from
    task timestamps. Lines are model-prefixed by their callers (`[<model>] …`),
    so the run log is grep-able per model. Logging must never break a run, so
    every write is best-effort. Thread-safe for parallel (per-model-thread) runs."""
    import threading
    lock = lock or threading.Lock()
    log_path = run_dir / "run.log"

    def wrapped(line):
        try:
            with lock, open(log_path, "a", encoding="utf-8") as fh:
                fh.write(f"{now_iso()} {line}\n")
        except OSError:
            pass
        progress(line)

    return wrapped


def run_suite(models: list[Model], tasks: list[Task], run_dir: Path | None = None,
              tag: str = "", progress=print, parallel: bool = False,
              cancel=None, force: bool = False) -> Path:
    """Serial (default) preserves timing fairness on a shared local GPU;
    parallel runs one thread per model, only timing-fair across *different*
    endpoints (e.g. one local + one cloud).

    Refuses while another run is executing. Every path (web panel, scout, CLI)
    goes through here, so the guard belongs here rather than in the job
    manager's in-memory lock.
    """
    import threading

    busy = None if force else active_run()
    if busy:
        raise RunInProgress(
            f"run {busy} is already executing. A second concurrent run competes "
            "for the same CPU and GPU that its timing-sensitive measurements "
            "depend on, and would corrupt both. Wait for it, stop it, or delete "
            "it if it crashed. (--force overrides.)")

    run_id = new_run_id()
    run_dir = run_dir or (config.RUNS_DIR / run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_dir.name, "tag": tag, "started": now_iso(),
        "suite_version": config.suite_version(),
        "env": env_snapshot(),
        "mode": "parallel" if parallel else "serial",
        "models": [m.name for m in models],
        "tasks": [{"id": t.id, "hash": t.content_hash, "tier": t.tier,
                   "category": t.category} for t in tasks],
        "finished": None,
    }
    write_json(run_dir / "run.json", manifest)

    from .util import keep_awake, read_json
    with keep_awake():
        _run_all(models, tasks, run_dir,
                 _persisting_progress(run_dir, progress), parallel, cancel)

    disk = read_json(run_dir / "run.json", {})
    for k in ("stopped_reason", "reset_at", "reset_hint", "stopped_models",
              "dropped_unscored"):
        if k in disk:
            manifest[k] = disk[k]
    manifest["finished"] = now_iso()
    write_json(run_dir / "run.json", manifest)
    return run_dir


def _run_all(models, tasks, run_dir, progress, parallel, cancel) -> None:
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
            run_model(run_dir, model, tasks, progress, cancel=cancel)
