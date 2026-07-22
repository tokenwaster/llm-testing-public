"""Model registry: one YAML file per model under models/.

Files starting with '_' are templates and are skipped. A model can also be
disabled with `enabled: false`.
"""

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
    extra: dict = field(default_factory=dict)
    enabled: bool = True
    color: str = ""
    show_in_reports: bool = True
    family: str = ""
    source_file: str = ""

    @property
    def family_name(self) -> str:
        """Grouping/colour family. Explicit yaml `family:` wins; `none` pins to
        No-family; empty infers from name/id."""
        fam = (self.family or "").strip()
        if fam.lower() == NO_FAMILY:
            return ""
        return fam or infer_family(self.name, self.model)

    @property
    def api_key(self) -> str | None:
        if self.key_env:
            return os.environ.get(self.key_env)
        return None

    def cost_usd(self, tokens_in: int | None, tokens_out: int | None,
                 cache_read: int | None = None,
                 cache_write: int | None = None) -> float | None:
        if tokens_in is None or tokens_out is None:
            return None
        in_rate = float(self.pricing.get("input_per_mtok", 0.0))
        out_rate = float(self.pricing.get("output_per_mtok", 0.0))
        cr, cw = cache_read or 0, cache_write or 0
        base = max(0, tokens_in - cr - cw)
        input_cost = (base + cw * 1.25 + cr * 0.10) / 1e6 * in_rate
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
    """{family_name: {"color": "#hex" | None}} from families.yaml. Missing = {}."""
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
    """Persist {family: {color}}. Machine-managed, so a plain dump is fine."""
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
    """Write a model's `family:` into its yaml. '' reverts to name-inference;
    the sentinel `none` pins it to No-family. Raises KeyError if not found."""
    f = _model_yaml(name, models_dir)
    if not f:
        raise KeyError(f"model '{name}' not found in {models_dir}")
    set_yaml_key(f, "family", family or "")


def set_model_color(name: str, color: str,
                    models_dir: Path = config.MODELS_DIR) -> None:
    """Write a model's `color:` (chart colour) into its yaml. '' clears it so the
    family colour (or auto palette) governs."""
    f = _model_yaml(name, models_dir)
    if not f:
        raise KeyError(f"model '{name}' not found in {models_dir}")
    set_yaml_key(f, "color", f"'{color}'" if color else "")


def infer_family(name: str, model_id: str = "") -> str:
    """Best-effort family from the name/id. Unrecognised => its own family (the
    name), so it still shows; it just won't cluster until a `family:` is set."""
    import re
    s = f"{name} {model_id}".lower()
    for fam, pat in _FAMILY_PATTERNS:
        if re.search(pat, s):
            return fam
    return name


def load_models(models_dir: Path = config.MODELS_DIR,
                include_disabled: bool = False) -> list[Model]:
    models: list[Model] = []
    for f in sorted(models_dir.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        raw = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        known = {k: v for k, v in raw.items() if k in Model.__dataclass_fields__}
        m = Model(**known)
        m.source_file = f.name
        if m.enabled or include_disabled:
            models.append(m)
    names = [m.name for m in models]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise ValueError(f"Duplicate model names in registry: {sorted(dupes)}")
    return models


def set_yaml_key(path: Path, key: str, value: str) -> None:
    """Set a top-level scalar in a model yaml by line edit — preserves the
    file's comments (unlike a parse/re-dump round trip)."""
    import re
    text = path.read_text(encoding="utf-8")
    if value == "":
        text = re.sub(rf"^{re.escape(key)}:.*(?:\r?\n)?", "", text,
                      count=1, flags=re.MULTILINE)
        path.write_text(text, encoding="utf-8")
        return
    line = f"{key}: {value}"
    pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
    if pattern.search(text):
        text = pattern.sub(line, text, count=1)
    else:
        text = text.rstrip("\n") + "\n" + line + "\n"
    path.write_text(text, encoding="utf-8")


def get_model(name: str, models_dir: Path = config.MODELS_DIR) -> Model:
    for m in load_models(models_dir):
        if m.name == name:
            return m
    raise KeyError(f"Model '{name}' not found in {models_dir}")


def set_enabled(name: str, value: bool) -> bool:
    """Flip a model's `enabled:` flag in its yaml; True if found. Scans
    config.MODELS_DIR live (not load_models, whose dir default is baked at
    import) and line-edits so comments survive."""
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
