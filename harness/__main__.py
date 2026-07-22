"""CLI entry point.

    python -m harness add lmstudio             # auto-register every LM Studio model
    python -m harness add claude [alias]       # register Claude via CLI (no API key)
    python -m harness list                     # show models & tasks
    python -m harness run [--models a,b] [--tasks pat] [--tier N] [--tag note]
    python -m harness serve [--port 8765]      # results site + run control panel
    python -m harness report                   # regenerate static HTML only
"""

import argparse
import fnmatch
import sys

from . import config, report
from .registry import load_models
from .runner import run_suite
from .tasks import load_tasks


def cmd_add(args) -> int:
    from . import discover
    if args.what == "lmstudio":
        created = discover.add_lmstudio(base_url=args.base_url)
    elif args.what == "claude":
        created = [p for p in [discover.add_claude(args.alias)] if p]
    else:
        print(f"error: unknown source '{args.what}' (use: lmstudio | claude)")
        return 2
    if created:
        print(f"\n{len(created)} model(s) registered. Next: python -m harness run")
    return 0


def cmd_list(_args) -> int:
    models = load_models()
    tasks = load_tasks()
    print(f"Models ({len(models)} enabled):")
    for m in models:
        loc = "local" if m.local else "cloud"
        print(f"  {m.name:32s} {m.provider:10s} {loc:6s} {m.model}"
              f"{'' if m.supports_tools else '  [no tools]'}")
    print(f"\nTasks ({len(tasks)}):")
    for t in tasks:
        print(f"  {t.id:28s} T{t.tier} {t.category:16s} "
              f"{t.scoring_type:7s} hash {t.content_hash}  {t.title}")
    return 0


def cmd_run(args) -> int:
    models = load_models()
    tasks = load_tasks()
    if args.models:
        wanted = [w.strip() for w in args.models.split(",")]
        missing = [w for w in wanted if not any(m.name == w for m in models)]
        if missing:
            print(f"error: unknown model(s): {missing}", file=sys.stderr)
            print(f"available: {[m.name for m in models]}", file=sys.stderr)
            return 2
        models = [m for m in models if m.name in wanted]
    if args.tasks == "hardened":
        tasks = [t for t in tasks if t.id in config.HARDENED_TASKS]
    elif args.tasks == "new":
        tasks = [t for t in tasks if t.id in config.NEW_TASKS]
    elif args.tasks:
        tasks = [t for t in tasks if fnmatch.fnmatch(t.id, args.tasks)
                 or fnmatch.fnmatch(t.category, args.tasks)]
    if args.tier:
        tasks = [t for t in tasks if t.tier == args.tier]
    if not models:
        print("error: no enabled models. Add a yaml to models/ "
              "(see the _example-*.yaml templates).", file=sys.stderr)
        return 2
    if not tasks:
        print("error: no tasks matched.", file=sys.stderr)
        return 2

    repeat = max(1, min(args.repeat, 10))
    print(f"Run: {len(models)} model(s) x {len(tasks)} task(s)"
          + (f" x {repeat} trials" if repeat > 1 else ""))
    from .util import keep_awake
    with keep_awake():
        for i in range(repeat):
            tag = args.tag if repeat == 1 else f"{args.tag} (trial {i + 1}/{repeat})".strip()
            if repeat > 1:
                print(f"\n===== trial {i + 1}/{repeat} =====")
            run_dir = run_suite(models, tasks, tag=tag)
    index = report.generate_all()
    print(f"\nRun complete: {run_dir}")
    print(f"View results: python -m harness serve   ->  http://127.0.0.1:8765")
    print(f"(static files: {index})")
    return 0


def _resolve_serve_port(args) -> int:
    """CLI --port wins for this run; with --save it becomes the persisted
    default; with neither, use the saved default (else 8765). Shared by the
    public viewer and the operator control server."""
    if args.port is not None:
        if getattr(args, "save", False):
            config.save_setting("serve_port", args.port)
            print(f"saved default serve port = {args.port} "
                  f"(runs here until changed; `harness serve` needs no --port now)")
        return args.port
    return config.serve_port()


def cmd_serve(args) -> int:
    """Read-only results website. The private operator layer (_control_cli)
    overrides this with the full run/watch/manage control panel when present."""
    from .viewer import serve
    serve(port=_resolve_serve_port(args))
    return 0


def cmd_report(args) -> int:
    if getattr(args, "dataset", None):
        from .archive import render_dataset
        render_dataset(args.dataset)
        return 0
    index = report.generate_all()
    print(f"Reports regenerated: {index}")
    return 0


def cmd_archive(args) -> int:
    from . import archive
    if args.list or not args.as_version:
        sets = archive.list_archives()
        if not sets:
            print("no archived datasets yet")
        for s in sets:
            print(f"  v{s['key']}: {s['runs']} run(s)"
                  + (" + tasks snapshot" if s["has_tasks_snapshot"] else ""))
        if not args.list and not args.as_version:
            print("\nusage: harness archive --as <major.minor>   "
                  "(archives ALL live runs under that key)")
        return 0
    n = archive.archive_current(args.as_version)
    report.generate_all()
    print(f"\nlive dataset is now empty (suite v{config.suite_version()}); "
          f"view the archived set any time:\n"
          f"  python -m harness report --dataset {args.as_version}")
    return 0 if n >= 0 else 1


def cmd_prices(args) -> int:
    """Re-read gateway list prices into the model yamls (catches drift, and a
    :free promo that has ended). Never rewrites already-recorded run costs."""
    from .prices import refresh
    refresh(apply=args.apply)
    return 0


def cmd_rescore(args) -> int:
    """Re-run checkers against SAVED workspaces (no model calls) — for when a
    checker bug or environment issue graded good outputs wrongly."""
    from .rescore import RunInProgress, rescore
    try:
        rescore(args.tasks, force=args.force)
    except RunInProgress as e:
        print(f"refusing to rescore: {e}")
        return 1
    return 0


def cmd_prune(args) -> int:
    """Delete individual task RESULTS from runs (e.g. results produced under a
    since-fixed unfair config). Dry-run by default; --yes to actually delete."""
    import fnmatch as _fn
    import shutil as _sh

    victims = []
    for run_dir in sorted(p for p in config.RUNS_DIR.iterdir() if p.is_dir()):
        if args.runs and not _fn.fnmatch(run_dir.name, args.runs):
            continue
        for model_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
            if args.models and not _fn.fnmatch(model_dir.name, args.models):
                continue
            for tdir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
                if _fn.fnmatch(tdir.name, args.tasks):
                    victims.append(tdir)
    if not victims:
        print("nothing matched.")
        return 0
    for v in victims:
        rel = v.relative_to(config.RUNS_DIR)
        print(f"  {'DELETE' if args.yes else 'would delete'}  {rel}")
    if not args.yes:
        print(f"\ndry run - {len(victims)} result(s) matched. "
              "Re-run with --yes to delete them.")
        return 0
    for v in victims:
        _sh.rmtree(v)
    report.generate_all()
    print(f"\n{len(victims)} result(s) deleted; reports regenerated.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        prog="harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="LLM Testing Suite - benchmark local (LM Studio) and hosted "
                    "(Anthropic, OpenAI, OpenRouter) models on the same tasks,\n"
                    "with full timing / token / retry / cost accounting and an "
                    "HTML results site.",
        epilog=(
            "typical loop:\n"
            "  harness add lmstudio          register every model LM Studio serves\n"
            "  harness add claude opus       register a Claude model (via the CLI)\n"
            "  harness run                   run all enabled models x all tasks\n"
            "  harness serve                 open the results site (default port 8765)\n"
            "  harness serve --port N --save set a different port as the default\n"
            "\n"
            "Every subcommand has its own flags - see `harness <command> --help` "
            "(e.g.\n`harness serve --help` for --port / --save, `harness run "
            "--help` for --models /\n--tasks / --tier). The operator commands "
            "(watch, scout, rename-model, review)\nappear only when the private "
            "operator layer is present; the public build ships\nthe read-only "
            "viewer (harness serve) and the run/report tools. See README.md."),
    )
    sub = p.add_subparsers(dest="cmd", required=True, metavar="<command>")

    pa = sub.add_parser("add", help="auto-register models (lmstudio | claude)")
    pa.add_argument("what", choices=["lmstudio", "claude"])
    pa.add_argument("alias", nargs="?", default="sonnet",
                    help="claude only: sonnet | opus | haiku (default sonnet)")
    pa.add_argument("--base-url", default="http://localhost:1234/v1",
                    help="lmstudio only: server URL")

    sub.add_parser("list", help="show enabled models and tasks")

    pr = sub.add_parser("run", help="run tasks against models")
    pr.add_argument("--models", help="comma-separated model names (default: all enabled)")
    pr.add_argument("--tasks", help="glob on task id or category (e.g. 'py-*' or "
                    "'reasoning'), 'hardened' for the curated repeat-run set, or "
                    "'new' for the v0.6.13 public-capability lanes")
    pr.add_argument("--tier", type=int, help="only tasks of this tier (1 or 2)")
    pr.add_argument("--tag", default="", help="label stored in the run manifest")
    pr.add_argument("--repeat", type=int, default=1,
                    help="run the whole suite N times; the trials aggregate "
                         "into each score (mean) and give it a σ")

    pp = sub.add_parser("report", help="regenerate static HTML from runs/")
    pp.add_argument("--dataset",
                    help="render an ARCHIVED dataset by key, e.g. 0.2")

    pav = sub.add_parser("archive",
                         help="archive all live runs under a version key")
    pav.add_argument("--as", dest="as_version", metavar="MAJOR.MINOR",
                     help="version key to archive the live runs under")
    pav.add_argument("--list", action="store_true",
                     help="list archived datasets")

    prs = sub.add_parser("rescore",
                         help="re-run checkers on saved workspaces (no model calls)")
    prs.add_argument("--tasks", required=True,
                     help="glob of task ids to rescore, e.g. 'web-*'")
    prs.add_argument("--force", action="store_true",
                     help="rescore even while a run is executing (its CPU "
                          "contention can wrongly zero timing-sensitive tasks)")

    ppc = sub.add_parser("prices",
                         help="refresh gateway list prices into the model yamls "
                              "(dry-run unless --apply)")
    ppc.add_argument("--apply", action="store_true",
                     help="write the new prices + stamp pricing_asof")

    ppr = sub.add_parser("prune",
                         help="delete individual task results (dry-run unless --yes)")
    ppr.add_argument("--tasks", required=True,
                     help="glob of task ids, e.g. 'py-004*'")
    ppr.add_argument("--models", help="glob of model names (default: all)")
    ppr.add_argument("--runs", help="glob of run ids (default: all)")
    ppr.add_argument("--yes", action="store_true",
                     help="actually delete (otherwise dry run)")

    psv = sub.add_parser("serve",
                         help="results website (read-only viewer); --port / --save")
    psv.add_argument("--port", type=int, default=None,
                     help="port to serve on (default: saved port, else 8765)")
    psv.add_argument("--save", action="store_true",
                     help="persist this --port as the default (settings.local.json)")

    commands = {"add": cmd_add, "list": cmd_list, "run": cmd_run,
                "report": cmd_report, "rescore": cmd_rescore,
                "archive": cmd_archive, "prune": cmd_prune, "serve": cmd_serve,
                "prices": cmd_prices}

    try:
        from . import _control_cli
        commands.update(_control_cli.register(sub))
    except ImportError:
        pass

    args = p.parse_args()
    return commands[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
