import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PUBLIC = {"config", "util", "registry", "tasks", "adapters", "scoring", "runner",
          "telemetry", "tools", "lmstudio", "gguf", "report", "fit", "archive",
          "assess", "rescore", "discover", "interfaces", "viewer"}
PRIVATE = {"watch", "jobs", "review", "scout", "rename"}


def test_public_modules_never_import_private_ones():
    offenders = []
    for mod in PUBLIC:
        f = ROOT / "harness" / f"{mod}.py"
        if not f.is_file():
            continue
        src = f.read_text(encoding="utf-8")
        imported = set(re.findall(r"from \.(\w+) import", src))
        imported |= {n.strip() for m in re.findall(r"from \. import ([\w, ]+)", src)
                     for n in m.split(",")}
        for p in imported & PRIVATE:
            offenders.append(f"{mod} imports {p}")
        if re.search(r"(from studio|import studio)\b", src):
            offenders.append(f"{mod} imports studio")
    assert not offenders, "public instrument reaches into the operator layer: " \
        + "; ".join(offenders)


def test_public_and_operator_builds_default_to_different_ports():
    from harness import config

    assert config.PUBLIC_SERVE_PORT != config.OPERATOR_SERVE_PORT
    expect = (config.OPERATOR_SERVE_PORT if config.is_operator_build()
              else config.PUBLIC_SERVE_PORT)
    assert config.default_serve_port() == expect


def test_model_links_survive_without_the_private_yaml():
    from harness import report

    ls = report._model_links("gemma-4-31b", None, local=True, publisher="google")
    urls = " ".join(l["url"] for l in ls)
    assert "huggingface.co/google/gemma-4-31b" in urls
    assert "openrouter.ai" in urls

    ls = report._model_links("glm-5.2", None, local=False)
    urls = " ".join(l["url"] for l in ls)
    assert "openrouter.ai" in urls and "huggingface.co" in urls

    ls = report._model_links("claude-cli-opus-4-8", None, local=False)
    assert len(ls) == 1 and "anthropic.com" in ls[0]["url"]


def test_data_browser_resolves_archived_runs(tmp_path, monkeypatch):
    from harness import config

    live = tmp_path / "runs"
    arch = tmp_path / "archive" / "v0.4" / "runs"
    (live / "R_LIVE" / "m" / "t").mkdir(parents=True)
    (arch / "R_ARCH" / "m" / "t").mkdir(parents=True)
    monkeypatch.setattr(config, "RUNS_DIR", live)
    monkeypatch.setattr(config, "ARCHIVE_DIR", tmp_path / "archive")

    assert config.resolve_run_data("R_LIVE/m/t")[0] == live
    assert config.resolve_run_data("R_ARCH/m/t")[0] == arch
    assert config.resolve_run_data("R_NOPE/x") is None
    assert config.resolve_run_data("")[0] == live


def test_operator_build_is_detected_by_the_private_cli_module():
    from harness import config

    assert config.is_operator_build() == (ROOT / "harness" / "_control_cli.py").is_file()
