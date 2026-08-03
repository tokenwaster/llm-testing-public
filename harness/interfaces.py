
import os

import httpx
import yaml

from . import config

INTERFACES_FILE = config.ROOT / "interfaces.yaml"

PRESETS = {
    "openrouter": {
        "kind": "openai", "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "note": "one key, every provider — pricing auto-filled from their catalog"},
    "ollama-cloud": {
        "kind": "openai", "base_url": "https://ollama.com/v1",
        "key_env": "OLLAMA_API_KEY",
        "note": "Ollama's hosted models (OpenAI-compatible endpoint)"},
    "openai": {
        "kind": "openai", "base_url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY", "note": "GPT models"},
    "groq": {
        "kind": "openai", "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY", "note": "fast open-weight hosting"},
    "kimi": {
        "kind": "openai", "base_url": "https://api.moonshot.ai/v1",
        "key_env": "MOONSHOT_API_KEY",
        "note": "Kimi / Moonshot first-party (kimi-k3 etc.). Name any model "
                "registered here distinctly from the OpenRouter-routed kimi-* "
                "— the model name is the aggregation key, so a shared name "
                "would pool two different routes into one identity"},
    "anthropic-api": {
        "kind": "anthropic", "base_url": "https://api.anthropic.com",
        "key_env": "ANTHROPIC_API_KEY",
        "note": "Claude via API key (claude-cli models already cover subscription)"},
    "custom": {
        "kind": "openai", "base_url": "", "key_env": "",
        "note": "any OpenAI-compatible endpoint"},
}

API_MODEL_TEMPLATE = """\
# Auto-registered from the {interface} interface via /backend
name: {name}
provider: {provider}
base_url: {base_url}
model: {model_id}
key_env: {key_env}
local: false
stream: {stream}
supports_tools: true          # set false if this model can't do tool calls (skips tier 2)
max_tokens: 32768   # uniform thinking budget across all models (fairness)
temperature: 0.2
pricing: {{ input_per_mtok: {in_price}, output_per_mtok: {out_price} }}
pricing_asof: {asof}          # snapshot date — refresh with `harness prices`
enabled: {enabled}
# OpenRouter routes to the cheapest upstream host by default — hosts differ in
# quantization and price. Actual billed cost + serving host (with its quant)
# are recorded per request automatically. Routing recipes (uncomment ONE):
#
# cheapest host at a fixed precision (recommended for benchmark runs):
# extra:
#   provider:
#     quantizations: ["fp8", "bf16", "fp16"]   # accept only these precisions
#     sort: "price"                            # cheapest among them
#
# pin one exact host:
# extra:
#   provider:
#     only: ["DeepInfra"]        # exact host name(s) from the model's page
#     allow_fallbacks: false
"""


def load_interfaces() -> list[dict]:
    try:
        data = yaml.safe_load(INTERFACES_FILE.read_text(encoding="utf-8")) or {}
        return list(data.get("interfaces") or [])
    except OSError:
        return []


def save_interfaces(interfaces: list[dict]) -> None:
    doc = ("# API interfaces for model discovery — managed on the /backend "
           "page.\n# Keys live in .env (gitignored), never in this file.\n"
           + yaml.safe_dump({"interfaces": interfaces},
                            sort_keys=False, allow_unicode=True))
    INTERFACES_FILE.write_text(doc, encoding="utf-8")


MASKED = ("…", "...", "*", "•")


def set_env_key(key_env: str, value: str) -> None:
    key_env = (key_env or "").strip()
    value = (value or "").strip().strip('"').strip("'")
    if not key_env:
        raise ValueError("no env var name given")
    if not value:
        raise ValueError(f"refusing to write an empty {key_env} — a blank save "
                         f"would silently revoke a working key")
    if any(tok in value for tok in MASKED):
        raise ValueError(f"that looks like a masked display value, not a key — "
                         f"{key_env} left unchanged")
    env_file = config.ROOT / ".env"
    raw = env_file.read_text(encoding="utf-8") if env_file.exists() else ""
    crlf = "\r\n" in raw
    lines = raw.replace("\r\n", "\n").split("\n")
    trailing = lines and lines[-1] == ""
    if trailing:
        lines.pop()
    new = f"{key_env}={value}"
    replaced = False
    for i, ln in enumerate(lines):
        if ln.strip().startswith(f"{key_env}="):
            if replaced:
                lines[i] = None
                continue
            lines[i] = new
            replaced = True
    lines = [ln for ln in lines if ln is not None]
    if not replaced:
        lines.append(new)
    body = "\n".join(lines) + "\n"
    env_file.write_text(body.replace("\n", "\r\n") if crlf else body,
                        encoding="utf-8")
    os.environ[key_env] = value


def key_status(key_env: str | None) -> bool:
    return bool(key_env and os.environ.get(key_env))


def list_remote_models(iface: dict) -> list[dict]:
    base = (iface.get("base_url") or "").rstrip("/")
    if not base:
        raise RuntimeError("interface has no base_url")
    key = os.environ.get(iface.get("key_env") or "")
    if iface.get("kind") == "anthropic":
        headers = {"x-api-key": key or "", "anthropic-version": "2023-06-01"}
        url = f"{base}/v1/models"
    else:
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        url = f"{base}/models"
    try:
        resp = httpx.get(url, headers=headers, timeout=20)
    except httpx.HTTPError as e:
        raise RuntimeError(f"cannot reach {base}: {e}") from e
    if resp.status_code in (401, 403):
        raise RuntimeError(f"auth failed — check {iface.get('key_env')} in .env")
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    out = []
    for e in resp.json().get("data", []):
        mid = e.get("id", "")
        if not mid or "embed" in mid.lower():
            continue
        entry = {"id": mid}
        pricing = e.get("pricing") or {}
        try:
            if pricing.get("prompt") is not None:
                entry["in_price"] = round(float(pricing["prompt"]) * 1e6, 4)
                entry["out_price"] = round(float(pricing["completion"]) * 1e6, 4)
        except (TypeError, ValueError):
            pass
        out.append(entry)
    return sorted(out, key=lambda m: m["id"])


def endpoint_quants(model_id: str) -> dict[str, str]:
    try:
        r = httpx.get(f"https://openrouter.ai/api/v1/models/{model_id}/endpoints",
                      timeout=15)
        if r.status_code != 200:
            return {}
        return {e.get("provider_name"): e.get("quantization") or "unknown"
                for e in (r.json().get("data") or {}).get("endpoints", [])
                if e.get("provider_name")}
    except (httpx.HTTPError, ValueError):
        return {}


def add_api_model(iface: dict, model_id: str,
                  in_price: float = 0.0, out_price: float = 0.0,
                  progress=print, enabled: bool = True,
                  name: str | None = None):
    from .discover import _slug
    name = _slug(name or model_id)
    path = config.MODELS_DIR / f"{name}.yaml"
    if path.exists():
        progress(f"  = {name}  (already registered, untouched)")
        return None
    if not in_price and not out_price:
        try:
            hit = next((e for e in list_remote_models(iface)
                        if e.get("id") == model_id), None)
            if hit and hit.get("in_price") is not None:
                in_price, out_price = hit["in_price"], hit["out_price"]
                progress(f"    price from {iface.get('name')} catalog: "
                         f"{in_price}/{out_price} per Mtok")
        except (RuntimeError, Exception):
            pass
    kind = iface.get("kind") or "openai"
    path.write_text(API_MODEL_TEMPLATE.format(
        interface=iface.get("name", "?"), name=name,
        provider="anthropic" if kind == "anthropic" else "openai",
        base_url=iface.get("base_url", ""), model_id=model_id,
        key_env=iface.get("key_env") or "null",
        stream="true" if kind != "anthropic" else "false",
        in_price=in_price or 0, out_price=out_price or 0,
        asof=__import__("datetime").date.today().isoformat(),
        enabled=str(enabled).lower()), encoding="utf-8")
    progress(f"  + {name}  ({model_id} via {iface.get('name')})")
    return path
