
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import config


@dataclass
class Model:
    name: str
    provider: str
    model: str
    base_url: str | None = None
    key_env: str | None = None
    local: bool = False
    stream: bool = True
    supports_tools: bool = True
    max_tokens: int = config.DEFAULT_MAX_TOKENS
    temperature: float = config.DEFAULT_TEMPERATURE
    context_length: int = 0
    pricing: dict = field(default_factory=lambda: {"input_per_mtok": 0.0, "output_per_mtok": 0.0})
    pricing_set: bool = False
    sampling: dict = field(default_factory=dict)
    sampling_profiles: dict = field(default_factory=dict)
    sampling_source: str = ""
    sampling_settable_yaml: bool | None = None
    sampling_unsettable_reason: str = ""
    effort: str | None = None
    thinking_off: bool = False
    thinking_off_in_yaml: bool = False
    extra: dict = field(default_factory=dict)
    enabled: bool = True
    color: str = ""
    show_in_reports: bool = True
    family: str = ""
    compare_key: str = ""
    source_file: str = ""

    @property
    def family_name(self) -> str:
        fam = (self.family or "").strip()
        if fam.lower() == NO_FAMILY:
            return ""
        return fam or infer_family(self.name, self.model)

    @property
    def api_key(self) -> str | None:
        if self.key_env:
            return os.environ.get(self.key_env)
        return None

    SAMPLING_KEYS = ("top_p", "top_k", "min_p", "top_a", "seed",
                     "repetition_penalty", "presence_penalty",
                     "frequency_penalty")

    CLI_PROVIDERS = ("claude-cli", "codex-cli")

    @property
    def is_cli(self) -> bool:
        return self.provider in self.CLI_PROVIDERS

    @property
    def sampling_settable(self) -> bool:
        if self.sampling_settable_yaml is not None:
            return bool(self.sampling_settable_yaml)
        return not self.is_cli

    EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")
    EFFORT_LEVELS_BY_PROVIDER = {
        "claude-cli": ("low", "medium", "high", "xhigh", "max"),
        "codex-cli": ("minimal", "low", "medium", "high", "xhigh"),
    }

    @property
    def effort_levels(self) -> tuple:
        return self.EFFORT_LEVELS_BY_PROVIDER.get(self.provider, ())

    @property
    def effort_settable(self) -> bool:
        return self.is_cli

    @property
    def effort_as_tested(self) -> str:
        if not self.effort_settable:
            return ""
        return self.effort or "inherited"

    @property
    def thinking_toggle_settable(self) -> bool:
        return self.provider == "openai" and not self.local

    @property
    def thinking_unsettable_reason(self) -> str:
        if self.thinking_toggle_settable:
            return ""
        if self.local:
            return ("LM Studio accepts the parameter and ignores it — measured: "
                    "enable_thinking=false left reasoning tokens unchanged, and "
                    "the endpoint returns 200 for a parameter that does not exist")
        return f"the {self.provider} transport has no reasoning toggle"

    @property
    def unsettable_reason(self) -> str:
        if self.sampling_settable:
            return ""
        if self.sampling_unsettable_reason.strip():
            return self.sampling_unsettable_reason.strip()
        if self.provider == "claude-cli":
            return ("the Claude CLI exposes no sampling flags, so nothing "
                    "configured here would be transmitted")
        if self.provider == "codex-cli":
            return ("the Codex CLI exposes no sampling flags, so nothing "
                    "configured here would be transmitted")
        return "this model does not accept sampling parameters"

    def resolved_sampling(self, category: str = "") -> tuple[dict, str]:
        prof = config.sampling_profile_for(category)
        over = (self.sampling_profiles or {}).get(prof) or {}
        merged = {**(self.sampling or {}), **over}
        return merged, (prof if over else "")

    def sampling_payload(self, category: str = "") -> dict:
        if not self.sampling_settable:
            return {}
        merged, _ = self.resolved_sampling(category)
        out = {}
        temp = merged.get("temperature", self.temperature)
        if temp is not None:
            out["temperature"] = temp
        for k in self.SAMPLING_KEYS:
            v = merged.get(k)
            if v is not None:
                out[k] = v
        return out

    def cost_usd(self, tokens_in: int | None, tokens_out: int | None,
                 cache_read: int | None = None,
                 cache_write: int | None = None) -> float | None:
        if tokens_in is None or tokens_out is None:
            return None
        in_rate = float(self.pricing.get("input_per_mtok", 0.0))
        out_rate = float(self.pricing.get("output_per_mtok", 0.0))
        cr, cw = cache_read or 0, cache_write or 0
        anthropic = self.provider in ("claude-cli", "anthropic")
        cr_mult = float(self.pricing.get("cache_read_mult",
                                         0.10 if anthropic else 1.0))
        cw_mult = float(self.pricing.get("cache_write_mult",
                                         1.25 if anthropic else 1.0))
        cr_rate = self.pricing.get("cache_read_per_mtok")
        cw_rate = self.pricing.get("cache_write_per_mtok")
        base = max(0, tokens_in - cr - cw)
        read_cost = (cr / 1e6 * float(cr_rate)) if cr_rate is not None \
            else (cr * cr_mult / 1e6 * in_rate)
        write_cost = (cw / 1e6 * float(cw_rate)) if cw_rate is not None \
            else (cw * cw_mult / 1e6 * in_rate)
        input_cost = base / 1e6 * in_rate + read_cost + write_cost
        return input_cost + tokens_out / 1e6 * out_rate


_FAMILY_PATTERNS = [
    ("Claude", r"claude|opus|sonnet|haiku|fable"),
    ("Gemma", r"gemma"), ("Qwen", r"qwen"), ("GPT", r"\bgpt|gpt-oss|-oss\b"),
    ("DeepSeek", r"deepseek"), ("GLM", r"\bglm"), ("Llama", r"llama"),
    ("Mistral", r"mistral|devstral|ministral|magistral"),
    ("Nemotron", r"nemotron"), ("MiniMax", r"minimax"),
    ("Cohere", r"cohere|command-|north-mini"), ("Hunyuan", r"hunyuan|hy3"),
    ("Grok", r"grok"), ("Phi", r"\bphi-?\d"), ("MiniCPM", r"minicpm"),
    ("Ornith", r"ornith"),
]


FAMILIES_FILE = config.ROOT / "families.yaml"
NO_FAMILY = "none"


def load_families() -> dict:
    try:
        data = yaml.safe_load(FAMILIES_FILE.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    out = {}
    for k, v in data.items():
        col = v.get("color") if isinstance(v, dict) else None
        out[str(k)] = {"color": col or None}
    return out


def save_families(families: dict) -> None:
    clean = {str(k): {"color": (v or {}).get("color") or None}
             for k, v in families.items() if str(k).strip()}
    FAMILIES_FILE.write_text(yaml.safe_dump(clean, sort_keys=True, allow_unicode=True),
                             encoding="utf-8")


def _model_yaml(name: str, models_dir: Path) -> Path | None:
    for f in sorted(models_dir.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        raw = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if raw.get("name") == name:
            return f
    return None


def set_model_family(name: str, family: str,
                     models_dir: Path = config.MODELS_DIR) -> None:
    f = _model_yaml(name, models_dir)
    if not f:
        raise KeyError(f"model '{name}' not found in {models_dir}")
    set_yaml_key(f, "family", family or "")


def set_model_color(name: str, color: str,
                    models_dir: Path = config.MODELS_DIR) -> None:
    import re
    f = _model_yaml(name, models_dir)
    if not f:
        raise KeyError(f"model '{name}' not found in {models_dir}")
    if color and not re.fullmatch(r"#[0-9A-Fa-f]{3,8}|[A-Za-z]{1,32}", color):
        raise ValueError(f"{color!r} is not a CSS colour (#hex or a name)")
    set_yaml_key(f, "color", f"'{color}'" if color else "")


def infer_family(name: str, model_id: str = "") -> str:
    import re
    s = f"{name} {model_id}".lower()
    for fam, pat in _FAMILY_PATTERNS:
        if re.search(pat, s):
            return fam
    return name


_YAML_CACHE: dict = {}


def reset_cache() -> None:
    _YAML_CACHE.clear()


def _model_fields(f: Path) -> dict:
    import copy
    try:
        st = f.stat()
        stamp = (st.st_mtime_ns, st.st_size)
    except OSError:
        stamp = None
    hit = _YAML_CACHE.get(f)
    if stamp is not None and hit is not None and hit[0] == stamp:
        return copy.deepcopy(hit[1])
    raw = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    raw["pricing_set"] = "pricing" in raw
    if "sampling_settable" in raw:
        raw["sampling_settable_yaml"] = raw.pop("sampling_settable")
    if raw.pop("thinking_off", None) is not None:
        raw["thinking_off_in_yaml"] = True
    known = {k: v for k, v in raw.items() if k in Model.__dataclass_fields__}
    if stamp is not None:
        _YAML_CACHE[f] = (stamp, copy.deepcopy(known))
    return known


def load_models(models_dir: Path = config.MODELS_DIR,
                include_disabled: bool = False) -> list[Model]:
    models: list[Model] = []
    for f in sorted(models_dir.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        m = Model(**_model_fields(f))
        m.source_file = f.name
        if m.enabled or include_disabled:
            models.append(m)
    names = [m.name for m in models]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise ValueError(f"Duplicate model names in registry: {sorted(dupes)}")
    return models


def set_yaml_key(path: Path, key: str, value: str) -> None:
    import re
    if "\n" in value or "\r" in value or "\n" in key or "\r" in key:
        raise ValueError(f"{key}: a yaml value written by the editor must be "
                         f"a single line")
    if not re.fullmatch(r"[A-Za-z_][\w\-]*", key):
        raise ValueError(f"{key!r} is not a valid yaml key")
    text = path.read_text(encoding="utf-8")
    if value == "":
        text = re.sub(rf"^{re.escape(key)}:.*(?:\r?\n)?", "", text,
                      count=1, flags=re.MULTILINE)
        path.write_text(text, encoding="utf-8")
        return
    pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
    found = pattern.search(text)
    if found:
        keep = re.search(r"\s+#.*$", found.group(0))
        line = f"{key}: {value}" + (keep.group(0) if keep else "")
        text = pattern.sub(lambda _: line, text, count=1)
    else:
        text = text.rstrip("\n") + "\n" + f"{key}: {value}" + "\n"
    path.write_text(text, encoding="utf-8")


def get_model(name: str, models_dir: Path = config.MODELS_DIR) -> Model:
    for m in load_models(models_dir):
        if m.name == name:
            return m
    raise KeyError(f"Model '{name}' not found in {models_dir}")


def set_enabled(name: str, value: bool) -> bool:
    import re
    for p in sorted(config.MODELS_DIR.glob("*.yaml")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        raw = yaml.safe_load(text) or {}
        if raw.get("name") != name:
            continue
        new = re.sub(r"^enabled:\s*\w+", f"enabled: {str(value).lower()}",
                     text, count=1, flags=re.M)
        if not re.search(r"^enabled:", new, flags=re.M):
            new = new.rstrip() + f"\nenabled: {str(value).lower()}\n"
        p.write_text(new, encoding="utf-8")
        return True
    return False
