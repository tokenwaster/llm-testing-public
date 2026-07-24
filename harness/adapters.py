"""Provider adapters: Anthropic, OpenAI-compatible (LM Studio, Ollama, vLLM,
OpenAI, OpenRouter, ...) and a mock, behind one neutral interface.

Neutral message format used by the runner:
    {"role": "user"|"assistant", "content": str,
     "tool_calls":  [{"id","name","args"}]        (assistant, optional)
    }
    {"role": "tool_results", "results": [{"id","name","output"}]}

Neutral tool format:
    {"name", "description", "parameters": <JSON schema object>}

Token usage comes from the provider's usage field — never estimated.
"""

import json
import re
import time
from dataclasses import dataclass, field

import httpx

from . import config
from .registry import Model
from .util import now_ms


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict


@dataclass
class ChatResult:
    text: str
    total_ms: float
    ttft_ms: float | None = None
    first_text_ms: float | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    cache_read_tokens: int | None = None
    cache_write_tokens: int | None = None
    reasoning_tokens: int | None = None
    stop_reason: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    turns: int | None = None
    cost_usd: float | None = None
    served_by: str | None = None


class AdapterError(Exception):
    def __init__(self, message: str, kind: str = "api", retryable: bool = True,
                 reset_at: float | None = None, reset_hint: str = "",
                 retry_after: float | None = None):
        super().__init__(message)
        self.kind = kind
        self.retryable = retryable
        self.reset_at = reset_at
        self.reset_hint = reset_hint
        self.retry_after = retry_after


_USAGE_LIMIT_PHRASES = (
    "session limit",
    "usage limit reached",
    "reached your usage limit",
    "exceeded your usage limit",
    "usage_limit_reached",
    "5-hour limit",
    "weekly limit",
    "daily limit",
)


def _detect_usage_limit(text: str) -> tuple[bool, float | None, str]:
    """Return (is_usage_limit, reset_epoch_or_None, reset_hint) for a CLI error blob."""
    if not text:
        return False, None, ""
    low = text.lower()
    if not any(p in low for p in _USAGE_LIMIT_PHRASES):
        return False, None, ""
    reset_at = None
    m = re.search(r"\|\s*(\d{9,13})", text)
    if m:
        ts = int(m.group(1))
        reset_at = ts / 1000 if ts > 1e12 else float(ts)
    hint = ""
    hm = re.search(r"reset[s]?\b[^\n]*", text, re.IGNORECASE)
    if hm:
        hint = hm.group(0).strip(" .").replace("�", "").replace("  ", " ").strip()
    return True, reset_at, hint


def _retry_after_s(headers, body: str) -> float | None:
    """Seconds the provider asked us to wait. Retry-After is the standard header
    (seconds, or an HTTP date); OpenRouter also puts a reset epoch in the 429
    body. Returns None when nobody said."""
    try:
        raw = (headers or {}).get("retry-after") or (headers or {}).get("Retry-After")
    except Exception:
        raw = None
    if raw:
        try:
            return max(0.0, float(str(raw).strip()))
        except ValueError:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(str(raw))
                return max(0.0, dt.timestamp() - time.time())
            except Exception:
                pass
    m = re.search(r'"?(?:X-RateLimit-Reset|reset)"?\s*[:=]\s*"?(\d{10,13})', body or "")
    if m:
        ts = int(m.group(1))
        ts = ts / 1000 if ts > 1e12 else float(ts)
        delta = ts - time.time()
        if 0 < delta <= 3600:
            return delta
    return None


def _classify_http(status: int, body: str, headers=None) -> AdapterError:
    if status in (401, 403):
        return AdapterError(f"HTTP {status}: {body[:300]}", kind="auth", retryable=False)
    if status == 429:
        return AdapterError(f"HTTP {status}: {body[:300]}", kind="rate_limit",
                            retryable=True,
                            retry_after=_retry_after_s(headers, body))
    if status >= 500:
        return AdapterError(f"HTTP {status}: {body[:300]}", kind="api", retryable=True)
    return AdapterError(f"HTTP {status}: {body[:300]}", kind="api", retryable=False)


class BaseAdapter:
    def __init__(self, model: Model):
        self.model = model

    def chat(self, messages: list[dict], system: str | None = None,
             tools: list[dict] | None = None, timeout_s: int = 180) -> ChatResult:
        raise NotImplementedError



class OpenAICompatAdapter(BaseAdapter):
    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        key = self.model.api_key
        if key:
            h["Authorization"] = f"Bearer {key}"
        return h

    def _url(self) -> str:
        base = (self.model.base_url or "https://api.openai.com/v1").rstrip("/")
        return f"{base}/chat/completions"

    def _to_openai_messages(self, messages: list[dict], system: str | None) -> list[dict]:
        out: list[dict] = []
        if system:
            out.append({"role": "system", "content": system})
        for m in messages:
            if m["role"] == "tool_results":
                for r in m["results"]:
                    out.append({"role": "tool", "tool_call_id": r["id"], "content": r["output"]})
            elif m["role"] == "assistant" and m.get("tool_calls"):
                out.append({
                    "role": "assistant",
                    "content": m.get("content") or None,
                    "tool_calls": [
                        {"id": tc["id"], "type": "function",
                         "function": {"name": tc["name"], "arguments": json.dumps(tc["args"])}}
                        for tc in m["tool_calls"]
                    ],
                })
            else:
                out.append({"role": m["role"], "content": m["content"]})
        return out

    def chat(self, messages, system=None, tools=None, timeout_s=180) -> ChatResult:
        payload: dict = {
            "model": self.model.model,
            "messages": self._to_openai_messages(messages, system),
            "max_tokens": self.model.max_tokens,
            "temperature": self.model.temperature,
            **self.model.extra,
        }
        if tools:
            payload["tools"] = [
                {"type": "function",
                 "function": {"name": t["name"], "description": t["description"],
                              "parameters": t["parameters"]}}
                for t in tools
            ]
        if self.model.stream and not tools:
            try:
                return self._chat_stream(payload, timeout_s)
            except AdapterError as e:
                if e.kind == "api" and "stream" in str(e).lower():
                    pass
                else:
                    raise
        return self._chat_plain(payload, timeout_s)

    def _post(self, payload: dict, timeout_s: int) -> httpx.Response:
        try:
            resp = httpx.post(self._url(), headers=self._headers(), json=payload,
                              timeout=httpx.Timeout(timeout_s, connect=15))
        except httpx.ConnectError as e:
            raise AdapterError(f"connect failed: {e}", kind="connect", retryable=True)
        except httpx.TimeoutException as e:
            raise AdapterError(f"timeout after {timeout_s}s: {e}", kind="timeout", retryable=True)
        except httpx.HTTPError as e:
            raise AdapterError(f"transport error: {type(e).__name__}: {e}",
                               kind="connect", retryable=True)
        if resp.status_code != 200:
            raise _classify_http(resp.status_code, resp.text, resp.headers)
        return resp

    def _chat_plain(self, payload: dict, timeout_s: int) -> ChatResult:
        t0 = now_ms()
        resp = self._post(payload, timeout_s)
        total = now_ms() - t0
        try:
            data = resp.json()
        except ValueError:
            raise AdapterError(f"non-JSON 200 response: {resp.text[:200]}",
                               kind="api", retryable=True)
        if data.get("error"):
            err = data["error"]
            raise AdapterError(f"in-body error: {err.get('message') or err}",
                               kind="api", retryable=True)
        if not data.get("choices"):
            raise AdapterError(f"200 response without choices: "
                               f"{str(data)[:200]}", kind="api", retryable=True)
        choice = data["choices"][0]
        msg = choice.get("message") or {}
        usage = data.get("usage") or {}
        tool_calls = [
            ToolCall(id=tc["id"], name=tc["function"]["name"],
                     args=_safe_json(tc["function"].get("arguments") or "{}"))
            for tc in (msg.get("tool_calls") or [])
        ]
        result = ChatResult(
            text=msg.get("content") or "",
            total_ms=total,
            ttft_ms=None,
            tokens_in=usage.get("prompt_tokens"),
            tokens_out=usage.get("completion_tokens"),
            stop_reason=choice.get("finish_reason"),
            tool_calls=tool_calls,
            cost_usd=usage.get("cost"),
            served_by=data.get("provider"),
        )
        _reject_degenerate(result, self.model.local)
        return result

    def _chat_stream(self, payload: dict, timeout_s: int) -> ChatResult:
        payload = {**payload, "stream": True, "stream_options": {"include_usage": True}}
        t0 = now_ms()
        ttft = None
        text_parts: list[str] = []
        tokens_in = tokens_out = reasoning_tokens = None
        reasoning_chars = 0
        stop_reason = None
        cost_usd = served_by = None
        guard = _LoopGuard()
        try:
            with httpx.stream("POST", self._url(), headers=self._headers(), json=payload,
                              timeout=httpx.Timeout(timeout_s, connect=15)) as resp:
                if resp.status_code != 200:
                    resp.read()
                    raise _classify_http(resp.status_code, resp.text, resp.headers)
                for line in resp.iter_lines():
                    if (now_ms() - t0) / 1000 > timeout_s:
                        raise AdapterError(
                            f"exceeded the {timeout_s}s budget "
                            f"(streamed {len(''.join(text_parts))} chars)",
                            kind="timeout", retryable=True)
                    if not line.startswith("data:"):
                        continue
                    chunk = line[5:].strip()
                    if chunk == "[DONE]":
                        break
                    data = _safe_json(chunk)
                    if not data:
                        continue
                    if data.get("provider"):
                        served_by = data["provider"]
                    if data.get("error"):
                        err = data["error"]
                        raise AdapterError(
                            f"in-stream error: {err.get('message') or err}",
                            kind="api", retryable=True)
                    usage = data.get("usage")
                    if usage:
                        tokens_in = usage.get("prompt_tokens", tokens_in)
                        tokens_out = usage.get("completion_tokens", tokens_out)
                        cost_usd = usage.get("cost", cost_usd)
                        rt = (usage.get("completion_tokens_details") or {}).get(
                            "reasoning_tokens")
                        rt = rt if rt is not None else usage.get("reasoning_tokens")
                        if rt is not None:
                            reasoning_tokens = rt
                    for choice in data.get("choices") or []:
                        delta = choice.get("delta") or {}
                        piece = delta.get("content")
                        reasoning = delta.get("reasoning_content") or delta.get("reasoning")
                        if reasoning:
                            reasoning_chars += len(reasoning)
                        if (piece or reasoning) and ttft is None:
                            ttft = now_ms() - t0
                        if piece:
                            text_parts.append(piece)
                        if guard.feed((piece or "") + (reasoning or "")):
                            raise AdapterError(
                                "repetition loop — the model is repeating one "
                                "short cycle without terminating (going nowhere); "
                                "aborted before the token ceiling",
                                kind="repetition_loop", retryable=False)
                        if choice.get("finish_reason"):
                            stop_reason = choice["finish_reason"]
        except httpx.ConnectError as e:
            raise AdapterError(f"connect failed: {e}", kind="connect", retryable=True)
        except httpx.TimeoutException as e:
            raise AdapterError(f"timeout after {timeout_s}s: {e}", kind="timeout", retryable=True)
        except httpx.HTTPError as e:
            raise AdapterError(f"stream broke mid-response: {type(e).__name__}: {e}",
                               kind="connect", retryable=True)
        if reasoning_tokens is None and reasoning_chars > 0:
            reasoning_tokens = round(reasoning_chars / 4)
        result = ChatResult(
            text="".join(text_parts),
            total_ms=now_ms() - t0,
            ttft_ms=ttft,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            reasoning_tokens=reasoning_tokens,
            stop_reason=stop_reason,
            cost_usd=cost_usd,
            served_by=served_by,
        )
        _reject_degenerate(result, self.model.local)
        return result


class _LoopGuard:
    """Detects a degenerate generation loop mid-stream (a bad local quant emits
    its full token ceiling as one repeating cycle and never stops).

    Fires only on strong evidence (a short cycle repeated MIN_REPS times over
    MIN_SPAN chars) so it never trips on legitimate repetitive output like
    tables. Watches the combined content+reasoning stream (a rumination loop may
    stay entirely in the think channel)."""
    WINDOW = 4096
    CHECK_EVERY = 512
    MIN_REPS = 24
    MIN_SPAN = 512
    MAX_PERIOD = 160

    def __init__(self) -> None:
        self._buf = ""
        self._since = 0

    def feed(self, piece: str) -> bool:
        """Accumulate a stream piece; return True if a loop is detected."""
        if not piece:
            return False
        self._buf = (self._buf + piece)[-self.WINDOW:]
        self._since += len(piece)
        if self._since < self.CHECK_EVERY:
            return False
        self._since = 0
        return self._looping(self._buf)

    @classmethod
    def _looping(cls, tail: str) -> bool:
        n = len(tail)
        for p in range(1, cls.MAX_PERIOD + 1):
            if n < p * cls.MIN_REPS:
                break
            cycle = tail[-p:]
            reps, i = 1, n - p
            while i - p >= 0 and tail[i - p:i] == cycle:
                reps += 1
                i -= p
            if reps >= cls.MIN_REPS and p * reps >= cls.MIN_SPAN:
                return True
        return False


def _reject_degenerate(res: "ChatResult", local: bool) -> None:
    """A 200 with no text, no tool calls, no usage and no stop reason is a
    server failure — surface it as an error, not a mysterious format miss.

    The cause depends on where it came from, and mislabelling it corrupts the
    attribution. For a LOCAL model (LM Studio) an empty 200 means the prompt
    overflowed the loaded context window: a real, non-retryable known-limit. For
    a CLOUD model it is a transient upstream hiccup — the provider accepted the
    request and returned nothing (kimi-k3 hit this on a 550-token prompt). That
    is infra, not the model's context, so it must retry and, if it persists,
    attribute to transport-drop — never context-overflow against a model whose
    window was nowhere near full."""
    if res.text or res.tool_calls or res.tokens_out is not None \
            or res.stop_reason is not None:
        return
    if local:
        raise AdapterError(
            "server returned an empty response — the prompt likely exceeded "
            "the loaded context window", kind="api", retryable=False)
    raise AdapterError(
        "empty response from the provider — no content, tokens, or stop reason "
        "(a transient upstream transport hiccup)", kind="transport",
        retryable=True)



class AnthropicAdapter(BaseAdapter):
    API_VERSION = "2023-06-01"

    def _headers(self) -> dict:
        key = self.model.api_key
        if not key:
            raise AdapterError(
                f"missing API key (set env var {self.model.key_env})", kind="auth", retryable=False)
        return {"Content-Type": "application/json", "x-api-key": key,
                "anthropic-version": self.API_VERSION}

    def _url(self) -> str:
        base = (self.model.base_url or "https://api.anthropic.com").rstrip("/")
        return f"{base}/v1/messages"

    def _to_anthropic_messages(self, messages: list[dict]) -> list[dict]:
        out: list[dict] = []
        for m in messages:
            if m["role"] == "tool_results":
                out.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": r["id"], "content": r["output"]}
                    for r in m["results"]
                ]})
            elif m["role"] == "assistant" and m.get("tool_calls"):
                content: list[dict] = []
                if m.get("content"):
                    content.append({"type": "text", "text": m["content"]})
                content += [{"type": "tool_use", "id": tc["id"], "name": tc["name"],
                             "input": tc["args"]} for tc in m["tool_calls"]]
                out.append({"role": "assistant", "content": content})
            else:
                out.append({"role": m["role"], "content": m["content"]})
        return out

    def chat(self, messages, system=None, tools=None, timeout_s=180) -> ChatResult:
        payload: dict = {
            "model": self.model.model,
            "messages": self._to_anthropic_messages(messages),
            "max_tokens": self.model.max_tokens,
            "temperature": self.model.temperature,
            **self.model.extra,
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = [{"name": t["name"], "description": t["description"],
                                 "input_schema": t["parameters"]} for t in tools]
        if self.model.stream and not tools:
            return self._chat_stream(payload, timeout_s)
        return self._chat_plain(payload, timeout_s)

    def _chat_plain(self, payload: dict, timeout_s: int) -> ChatResult:
        t0 = now_ms()
        try:
            resp = httpx.post(self._url(), headers=self._headers(), json=payload,
                              timeout=httpx.Timeout(timeout_s, connect=15))
        except httpx.ConnectError as e:
            raise AdapterError(f"connect failed: {e}", kind="connect", retryable=True)
        except httpx.TimeoutException as e:
            raise AdapterError(f"timeout after {timeout_s}s: {e}", kind="timeout", retryable=True)
        except httpx.HTTPError as e:
            raise AdapterError(f"transport error: {type(e).__name__}: {e}",
                               kind="connect", retryable=True)
        if resp.status_code != 200:
            raise _classify_http(resp.status_code, resp.text, resp.headers)
        total = now_ms() - t0
        data = resp.json()
        text_parts, tool_calls = [], []
        for block in data.get("content", []):
            if block["type"] == "text":
                text_parts.append(block["text"])
            elif block["type"] == "tool_use":
                tool_calls.append(ToolCall(id=block["id"], name=block["name"],
                                           args=block.get("input") or {}))
        usage = data.get("usage") or {}
        return ChatResult(
            text="".join(text_parts),
            total_ms=total,
            tokens_in=usage.get("input_tokens"),
            tokens_out=usage.get("output_tokens"),
            stop_reason=data.get("stop_reason"),
            tool_calls=tool_calls,
        )

    def _chat_stream(self, payload: dict, timeout_s: int) -> ChatResult:
        payload = {**payload, "stream": True}
        t0 = now_ms()
        ttft = None
        text_parts: list[str] = []
        tokens_in = tokens_out = None
        stop_reason = None
        try:
            with httpx.stream("POST", self._url(), headers=self._headers(), json=payload,
                              timeout=httpx.Timeout(timeout_s, connect=15)) as resp:
                if resp.status_code != 200:
                    resp.read()
                    raise _classify_http(resp.status_code, resp.text, resp.headers)
                for line in resp.iter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = _safe_json(line[5:].strip())
                    if not data:
                        continue
                    etype = data.get("type")
                    if etype == "message_start":
                        tokens_in = (data.get("message", {}).get("usage") or {}).get("input_tokens")
                    elif etype == "content_block_delta":
                        piece = (data.get("delta") or {}).get("text")
                        if piece:
                            if ttft is None:
                                ttft = now_ms() - t0
                            text_parts.append(piece)
                    elif etype == "message_delta":
                        usage = data.get("usage") or {}
                        tokens_out = usage.get("output_tokens", tokens_out)
                        stop_reason = (data.get("delta") or {}).get("stop_reason", stop_reason)
        except httpx.ConnectError as e:
            raise AdapterError(f"connect failed: {e}", kind="connect", retryable=True)
        except httpx.TimeoutException as e:
            raise AdapterError(f"timeout after {timeout_s}s: {e}", kind="timeout", retryable=True)
        except httpx.HTTPError as e:
            raise AdapterError(f"stream broke mid-response: {type(e).__name__}: {e}",
                               kind="connect", retryable=True)
        return ChatResult(
            text="".join(text_parts),
            total_ms=now_ms() - t0,
            ttft_ms=ttft,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            stop_reason=stop_reason,
        )



class ClaudeCLIAdapter(BaseAdapter):
    """Runs `claude -p` per request. Every call spawns a fresh subprocess (no
    history) in an empty sandbox with file/shell/web tools disallowed, so the
    model can only see the prompt.

    Single-turn only (tier 1; set supports_tools: false in the yaml). No
    streaming, so ttft_ms is None.
    """

    DISALLOWED = ("Bash", "Read", "Write", "Edit", "Glob", "Grep",
                  "WebFetch", "WebSearch", "Task", "NotebookEdit")

    def chat(self, messages, system=None, tools=None, timeout_s=180) -> ChatResult:
        import shutil
        import subprocess
        import tempfile

        if tools:
            raise AdapterError("claude-cli adapter is single-turn text only "
                               "(set supports_tools: false)", kind="api", retryable=False)
        exe = shutil.which("claude")
        if not exe:
            raise AdapterError("claude CLI not found on PATH", kind="connect", retryable=False)
        prompt = "\n\n".join(m["content"] for m in messages if m["role"] == "user")
        cmd = [exe, "-p", "--output-format", "json", "--max-turns", "1",
               "--model", self.model.model,
               "--disallowedTools", ",".join(self.DISALLOWED)]
        if system:
            cmd += ["--append-system-prompt", system]
        cmd += list(self.model.extra.get("cli_args", []))

        with tempfile.TemporaryDirectory(prefix="llmtest-sandbox-",
                                         ignore_cleanup_errors=True) as sandbox:
            t0 = now_ms()
            data = _stream_claude_cli(cmd, prompt, sandbox, timeout_s)
        return self._parse_result(data, now_ms() - t0)

    def chat_agentic(self, prompt: str, workspace, max_turns: int,
                     timeout_s: int) -> ChatResult:
        """Tier-2: Claude Code works in the task workspace with its own tools
        (file ops + running python). Fresh session, cwd=workspace, so it sees
        only the task's files."""
        import shutil

        exe = shutil.which("claude")
        if not exe:
            raise AdapterError("claude CLI not found on PATH", kind="connect",
                               retryable=False)
        cmd = [exe, "-p", "--output-format", "json",
               "--model", self.model.model,
               "--max-turns", str(max_turns),
               "--permission-mode", "acceptEdits",
               "--allowedTools", "Read,Write,Edit,Glob,Grep,Bash(python:*)",
               "--disallowedTools", "WebFetch,WebSearch,Task,NotebookEdit"]
        t0 = now_ms()
        data = _stream_claude_cli(cmd, prompt, str(workspace), timeout_s)
        return self._parse_result(data, now_ms() - t0)

    def _parse_result(self, data: dict, total_ms: float) -> ChatResult:
        if not data or data.get("is_error"):
            detail = (data.get("result") if data else "") or ""
            if not detail and data:
                try:
                    dump = json.dumps(data)[:300]
                except (TypeError, ValueError):
                    dump = str(data)[:300]
                detail = str(data.get("subtype") or data.get("error") or dump)
            is_limit, reset_at, reset_hint = _detect_usage_limit(str(detail))
            if is_limit:
                disp = reset_hint or (f"resets {_fmt_epoch(reset_at)}"
                                      if reset_at else "")
                raise AdapterError(
                    "Claude subscription usage limit reached"
                    + (f" — {disp}" if disp else ""),
                    kind="usage_limit", retryable=False,
                    reset_at=reset_at, reset_hint=reset_hint)
            raise AdapterError(f"claude CLI failed: {str(detail)[:300]}",
                               kind="api", retryable=True)
        usage = data.get("usage") or {}
        cache_read = usage.get("cache_read_input_tokens") or 0
        cache_write = usage.get("cache_creation_input_tokens") or 0
        tokens_in = (usage.get("input_tokens") or 0) + cache_read + cache_write or None
        requested = getattr(getattr(self, "model", None), "model", "") or ""
        served = _resolve_served_model(data.get("modelUsage"), requested)
        return ChatResult(
            text=data.get("result") or "",
            total_ms=total_ms,
            ttft_ms=None,
            first_text_ms=data.get("_first_text_ms"),
            tokens_in=tokens_in,
            tokens_out=usage.get("output_tokens"),
            cache_read_tokens=cache_read or None,
            cache_write_tokens=cache_write or None,
            stop_reason=data.get("subtype"),
            turns=data.get("num_turns"),
            served_by=served,
        )



class MockAdapter(BaseAdapter):
    """Echoes a canned response; used to verify the whole pipeline offline."""

    def chat(self, messages, system=None, tools=None, timeout_s=180) -> ChatResult:
        prompt = messages[-1].get("content", "") if messages else ""
        if "ANSWER:" in prompt:
            text = "Let me think about this.\nANSWER: 42"
        elif "solution.py" in prompt:
            text = ("Here is my solution.\n\n```python\n"
                    "def placeholder():\n    return None\n```\n")
        else:
            text = "Mock response for pipeline testing."
        return ChatResult(text=text, total_ms=5.0, ttft_ms=1.0,
                          tokens_in=len(prompt) // 4, tokens_out=len(text) // 4,
                          stop_reason="stop")


def _safe_json(text: str) -> dict:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}


from .util import terminate_tree as _terminate_tree


def _stream_claude_cli(cmd: list[str], prompt: str, cwd: str,
                       timeout_s: int) -> dict:
    """Run `claude -p --output-format stream-json` and watch it work.

    Streaming (over `--output-format json`, which emits nothing until exit) lets
    us record time-to-first-answer-token and enforce the total `timeout_s`
    deadline. It does NOT stop the model for being silent: the CLI exposes only
    answer text and the final result — never the thinking content — so we cannot
    tell genuine extended thinking from a loop, and silence alone means only
    "needs a bigger window", never a spiral. A model that thinks the whole window
    without answering hits `timeout_s` (a window/time result), and the operator
    widens the window from the measured first-answer times. Real spirals — a
    repeating cycle going nowhere — are only detectable where the token stream is
    visible (_LoopGuard on local/API models), not here.

    Returns the CLI's final `result` event (same shape as --output-format json).
    """
    import json as _json
    import queue as _queue
    import subprocess
    import threading

    cmd = list(cmd)
    for i, c in enumerate(cmd):
        if c == "--output-format" and i + 1 < len(cmd):
            cmd[i + 1] = "stream-json"
            break
    if "--verbose" not in cmd:
        cmd.append("--verbose")

    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, cwd=cwd, text=True,
        encoding="utf-8", errors="replace", bufsize=1,
        start_new_session=True)

    lines: _queue.Queue = _queue.Queue()

    def _pump():
        try:
            for line in proc.stdout:
                lines.put(line)
        finally:
            lines.put(None)

    threading.Thread(target=_pump, daemon=True).start()
    try:
        proc.stdin.write(prompt)
        proc.stdin.close()
    except OSError:
        pass

    t0 = now_ms()
    saw_text = False
    first_text_ms: float | None = None
    final: dict | None = None
    tail: list[str] = []

    try:
        while True:
            elapsed = (now_ms() - t0) / 1000
            if elapsed > timeout_s:
                raise AdapterError(
                    f"claude CLI exceeded the {timeout_s}s budget",
                    kind="timeout", retryable=True)
            try:
                line = lines.get(timeout=1.0)
            except _queue.Empty:
                continue
            if line is None:
                break
            line = line.strip()
            if not line:
                continue
            tail.append(line[:200])
            del tail[:-5]
            ev = _safe_json(line)
            if not ev:
                continue
            kind = ev.get("type")
            if kind == "assistant":
                content = (ev.get("message") or {}).get("content") or []
                if any((b.get("text") or "").strip()
                       for b in content if isinstance(b, dict)):
                    if not saw_text:
                        first_text_ms = now_ms() - t0
                    saw_text = True
            elif kind == "result":
                final = ev
    finally:
        _terminate_tree(proc)
        try:
            proc.wait(timeout=10)
        except Exception:
            pass

    if final is None:
        raise AdapterError(
            "claude CLI produced no result event: " + " | ".join(tail)[:300],
            kind="api", retryable=True)
    final["_first_text_ms"] = first_text_ms
    return final


def _resolve_served_model(model_usage, requested: str) -> str | None:
    """Which model actually answered, from the CLI's `modelUsage` block.

    Claude Code bills a small helper model alongside the real one, so modelUsage
    routinely holds two entries; picking by tokens or alphabetically selects the
    helper. Match the requested alias's family first, else fall back to the
    priciest entry (the real work is the expensive one).
    """
    if not isinstance(model_usage, dict) or not model_usage:
        return None
    if len(model_usage) == 1:
        return next(iter(model_usage))
    req = (requested or "").lower()
    for name in model_usage:
        if req and req in name.lower():
            return name
    return max(model_usage.items(),
               key=lambda kv: (kv[1] or {}).get("costUSD") or 0)[0]


def _fmt_epoch(epoch: float | None) -> str:
    """UNIX epoch -> local 'Mon 15:04' string, or '' when unknown."""
    if not epoch:
        return ""
    from datetime import datetime
    try:
        return datetime.fromtimestamp(epoch).strftime("%a %H:%M")
    except (ValueError, OverflowError, OSError):
        return ""


ADAPTERS = {
    "openai": OpenAICompatAdapter,
    "anthropic": AnthropicAdapter,
    "claude-cli": ClaudeCLIAdapter,
    "mock": MockAdapter,
}


def make_adapter(model: Model) -> BaseAdapter:
    try:
        return ADAPTERS[model.provider](model)
    except KeyError:
        raise ValueError(f"Unknown provider '{model.provider}' for model '{model.name}'. "
                         f"Valid: {sorted(ADAPTERS)}")
