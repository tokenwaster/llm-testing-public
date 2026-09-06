"""Single public release boundary, shared by export, publish and tests."""
from pathlib import Path
import re


_CREDENTIALS = re.compile(
    rb"(?:sk-(?:proj-|ant-api\d\d-|or-v1-)?[A-Za-z0-9_-]{32,}"
    rb"|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}"
    rb"|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    rb"|Bearer [A-Za-z0-9._~-]{40,})"
)
_SENSITIVE_NAMES = {'.env', 'interfaces.yaml', 'settings.local.json', 'secrets.local.json',
                    'mirror.json', 'id_rsa', 'id_ed25519', 'credentials.json'}


def guard_tree(root: Path) -> None:
    """Inspect final bytes, never print a credential in error output."""
    root = root.resolve()
    failures = []
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if {'.git', '__pycache__', '.pytest_cache'} & set(rel.parts):
            continue
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            failures.append(f'{rel}: linked path')
            continue
        if not path.is_file():
            continue
        if (path.name.lower() in _SENSITIVE_NAMES or path.name.lower().startswith('.env.')
                or path.name.endswith('.local.json') or path.suffix.lower() in {'.pem', '.key', '.pfx'}
                or rel.parts[0] in {'studio', 'watch', 'scouts', 'private'}
                or (rel.parts[0] == 'harness' and path.stem in PRIVATE_HARNESS)
                or rel.as_posix() == 'harness/_control_cli.py'):
            failures.append(f'{rel}: private file')
            continue
        with path.open('rb') as stream:
            tail = b''
            while chunk := stream.read(1024 * 1024):
                if _CREDENTIALS.search(tail + chunk):
                    failures.append(f'{rel}: credential-shaped content')
                    break
                tail = chunk[-512:]
    if failures:
        raise RuntimeError('Public export refused:\n' + '\n'.join(failures[:30]))

PUBLIC_HARNESS = [
    "__init__.py", "__main__.py", "config.py", "util.py", "registry.py",
    "tasks.py", "adapters.py", "scoring.py", "runner.py", "telemetry.py",
    "tools.py", "lmstudio.py", "gguf.py", "report.py", "fit.py", "archive.py",
    "assess.py", "rescore.py", "discover.py", "interfaces.py", "viewer.py",
    "prices.py",
    "validate.py",
    "mirror.py",
    "thinking.py",
    "apicost.py",
    "budget.py", "boundary.py", "security.py", "experience.py",
]


PRIVATE_HARNESS = ["watch", "jobs", "review", "scout", "rename", "publish"]


PRIVATE_TOPLEVEL = ["studio"]


PUBLIC_TREES = ["tasks", "tasks-refs", "tests", "runs", "archive",
                "special", "harness/presentation"]


PUBLIC_FILES = ["CHANGELOG.md", "LICENSE", "requirements.txt",
                "harness.ps1", "pytest.ini", "SUITE_VERSION", "directives.yaml",
                "families.yaml", ".gitignore"]


PUBLIC_DOCS = ["docs/PUBLIC-RELEASE.md"]


NEVER = {".git", ".env", "interfaces.yaml", "CONTENT-PLAN.md", "watch", "scouts",
         "models", "__pycache__", ".pytest_cache", "private",
         "settings.local.json", "secrets.local.json", "mirror.json",
         "test_watch.py", "test_studio.py", "test_jobs.py", "test_hardening.py",
         "test_staging.py",
         "test_review_score.py", "test_review_configs.py",
         "test_mirror_leg.py", "test_mirror.py",
         "test_export_complete.py",
         "test_thinking_probe.py", "test_probe_topup.py",
         "test_operator_style.py",
         "test_spend_ui.py"}


def _verify_no_private_imports(dst: Path) -> list[str]:
    import ast

    priv_h, priv_t = set(PRIVATE_HARNESS), set(PRIVATE_TOPLEVEL)
    hits: list[str] = []

    def bad(mod: str | None, names, level: int) -> str | None:
        mod = mod or ""
        parts = mod.split(".") if mod else []
        if level and parts and parts[0] in priv_h:
            return parts[0]
        if level and not parts:
            for n in names:
                if n in priv_h:
                    return n
        if parts[:1] == ["harness"] and parts[1:2] and parts[1] in priv_h:
            return parts[1]
        if parts[:1] == ["harness"] and not parts[1:]:
            for n in names:
                if n in priv_h:
                    return n
        if parts and parts[0] in priv_t:
            return parts[0]
        return None

    DATA = {"runs", "archive", "reports", "special"}
    for py in sorted(dst.rglob("*.py")):
        rel = py.relative_to(dst)
        if DATA & set(rel.parts):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError as e:
            hits.append(f"{rel}: unparseable ({e})")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    p = a.name.split(".")
                    if p[0] in priv_t or (p[:1] == ["harness"] and p[1:2]
                                          and p[1] in priv_h):
                        hits.append(f"{py.relative_to(dst)}:{node.lineno}: "
                                    f"import {a.name}")
            elif isinstance(node, ast.ImportFrom):
                who = bad(node.module, [a.name for a in node.names], node.level)
                if who:
                    hits.append(f"{py.relative_to(dst)}:{node.lineno}: "
                                f"from {'.' * node.level}{node.module or ''} "
                                f"imports private '{who}'")
    return hits



LEAK_PATTERNS = [
    (re.compile(rb'"user_id"\s*:\s*"user_[A-Za-z0-9]+"'), b'"user_id":"[redacted]"'),
    (re.compile(rb'workspaces/default/keys/[0-9a-f]+'), b'workspaces/default/keys/[redacted]'),
    (re.compile(rb'(?i)([\\/]+Users[\\/]+)bghur'), rb'\1user'),
    (re.compile(rb'bghurt@gmail\.com'), b'user@example.com'),
]
SCRUB_SUFFIXES = {".log", ".json", ".jsonl", ".txt", ".md", ".html", ".css", ".js"}


def _scrub(data: bytes) -> tuple[bytes, int]:
    data, n = _CREDENTIALS.subn(b'[credential redacted]', data)
    for pat, repl in LEAK_PATTERNS:
        data, k = pat.subn(repl, data)
        n += k
    return data, n
