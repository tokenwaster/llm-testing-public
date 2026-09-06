"""Public decisions, examples and downloadable evidence derived from run data."""
import csv
import io
import json
import re
import hashlib
from pathlib import Path
from statistics import fmean

from . import config
from .security import isolated_preview, json_for_script, preview_hashes


def model_name(name: str) -> str:
    transport = ''
    for prefix, label in (('claude-cli-', 'CLI'), ('codex-cli-', 'CLI'), ('claude-api-', 'API')):
        if name.startswith(prefix):
            name = name[len(prefix):]
            if prefix.startswith('claude'):
                name = 'claude-' + name
            transport = f' ({label})'
            break
    name = re.sub(r'(?<=\d)-(?=\d+(?:-|$))', '.', name)
    words = name.replace('-', ' ').split()
    upper = {'gpt', 'glm', 'api', 'cli', 'oss'}
    return ' '.join(w.upper() if w in upper else w.capitalize() for w in words) + transport


def _score(entry):
    s = entry.get('score') or {}
    return s.get('score') if s.get('status') == 'scored' else None


def dataset(runs, tdefs):
    from . import report
    td = report.collect_task_data(runs)
    manifests = {r['run_id']: r['manifest'] for r in runs}
    _, hidden = report._model_prefs()
    models = sorted({m for tid, info in td.items() if tid in tdefs for m in info['agg']} - hidden)
    data = {}
    for model in models:
        cells = {}
        for tid, info in td.items():
            if tid not in tdefs or model not in info['agg']:
                continue
            e = info['agg'][model]
            history = [h for h in info['history'] if h['model'] == model and _score(h) is not None]
            signatures = set()
            for h in history:
                manifest = manifests[h['run_id']]
                spec = (manifest.get('model_sampling') or {}).get(model) or {}
                effort = h.get('effort_used')
                if not spec.get('max_tokens') or effort == 'inherited':
                    signatures.add(None)
                    continue
                signatures.add(json.dumps({
                    'task_hash': h.get('task_hash'), 'budget': spec['max_tokens'],
                    'sampling': h.get('sampling_used'), 'effort': effort,
                    'mode': manifest.get('mode'), 'tier': h.get('tier'),
                    'transport': 'cli' if report._is_subscription([h]) else 'api',
                    'local': bool(h.get('model_meta', {}).get('local')),
                }, sort_keys=True))
            condition = next(iter(signatures)) if len(signatures) == 1 and None not in signatures else None
            if not history or any(h.get('task_hash') != tdefs[tid].content_hash for h in history):
                condition = None
            cost = None if report._is_subscription([e]) else e.get('cost_usd')
            if any(h.get('cost_usd') is None for h in history):
                cost = None
            cells[tid] = {'score': _score(e), 'n': len(history), 'sigma': e.get('score_sigma'),
                          'wall': e.get('wall_ms'), 'cost': cost, 'condition': condition,
                          'run': e['run_id'], 'hash': e.get('task_hash'),
                          'receipt': report._receipt_url(e['run_id'], model, tid)}
        entries = [td[t]['agg'][model] for t in cells]
        if not entries:
            continue
        meta = entries[-1].get('model_meta') or {}
        local = bool(meta.get('local'))
        peaks = [e.get('model_meta', {}).get('gpu', {}).get('vram_peak_mb') for e in entries]
        peak = max((v for v in peaks if v is not None), default=None)
        data[model] = {'name': model_name(model), 'slug': report._slug_name(model),
                       'kind': 'local' if local else ('cli' if report._is_subscription(entries) else 'api'),
                       'vram': round(peak / 1024, 1) if peak else None, 'cells': cells}
    return {'models': data,
            'tasks': {tid: {'name': t.title, 'category': t.category, 'hash': t.content_hash} for tid, t in tdefs.items()},
            'version': (runs[-1]['manifest'].get('suite_version') if runs else config.suite_version()),
            'asof': max((r['manifest'].get('finished') or r['manifest'].get('started') or '' for r in runs), default=''),
            'aggregation': 'Mean of every scored run per model/task; unscored attempts excluded.'}


STORIES = [
    {'id': 'maze-memory', 'task': 'web-002-maze', 'title': 'A moving bot can still be stuck',
     'question': 'Does the maze explorer remember where it has already been?',
     'expected': 'All 24 bots must reach the exit, follow connected passages and stop revisiting exhausted paths. Animation alone is not success.',
     'lesson': 'For agent work, ask whether the system makes progress and knows when to stop. A convincing animation cannot establish that.',
     'checks': 'test_all_bots_finish_and_timer_freezes, test_movement_continuity, test_dead_end_memory'},
    {'id': 'spreadsheet-recalc', 'task': 'web-006-spreadsheet', 'title': 'The answer changes when the input changes',
     'question': 'Does the spreadsheet remain correct after an edit?',
     'expected': 'Changing an upstream cell must update its dependants, respect expression precedence and report circular references.',
     'lesson': 'A correct first answer is only the start. Stateful tools must keep related answers consistent when a user changes their mind.',
     'checks': 'test_transitive_recalc, test_cycle_detection, test_dom_recalc_and_cycle'},
    {'id': 'expense-validation', 'task': 'web-005-expense', 'title': 'A useful form must reject bad data',
     'question': 'Does the expense tracker protect the total from invalid entries?',
     'expected': 'Valid expenses must survive reloads; invalid inputs must be rejected and filters must update the visible records and totals.',
     'lesson': 'Check what happens at the edges of a workflow: empty values, invalid entries, edits and reloads. That is where an attractive demo becomes a usable tool.',
     'checks': 'test_invalid_amount_rejected, test_valid_expenses_added, test_persistence_across_reload'},
]


def story_cases(info, tdef, base: Path):
    """Every card is ONE actual attempt, never an aggregate dressed as an app."""
    from . import report
    cases = []
    for e in info['history']:
        if _score(e) is None or e.get('task_hash') != tdef.content_hash:
            continue
        folder = base / e['run_id'] / e['model'] / tdef.id
        app = folder / 'workspace' / 'app.html'
        detail = (e.get('score') or {}).get('detail') or ''
        failures = list(dict.fromkeys(line.strip() for line in detail.splitlines()
                                     if line.startswith(('E ', 'FAILED '))))[:8]
        cases.append({'model': e['model'], 'name': model_name(e['model']), 'run': e['run_id'],
                      'score': _score(e), 'hash': e.get('task_hash'),
                      'summary': (e.get('score') or {}).get('summary') or 'Scored attempt',
                      'failures': failures,
                      'output': report.last_response_text(e['run_id'], e['model'], tdef.id, 8000),
                      'app': isolated_preview(app.read_text(encoding='utf-8', errors='replace')) if app.is_file() else '',
                      'receipt': report._receipt_url(e['run_id'], e['model'], tdef.id)})
    return sorted(cases, key=lambda c: (-c['score'], c['model'], c['run']))


def write_experience(out: Path, runs, tdefs, key, label, write):
    from . import report
    d = dataset(runs, tdefs)
    common = {'nav': report._nav(), 'brand': report._brand(), 'css': report.BASE_CSS,
              'experience_css': report._asset('experience.css'),
              'shared_js': report._asset('experience.js'), 'data_json': json_for_script(d),
              'version': d['version'], 'asof': d['asof'][:10], 'label': label}
    write(out / 'choose.html', report._compiled(report._asset('choose.html')).render(**common))
    downloads = out / 'downloads'
    downloads.mkdir(exist_ok=True)
    (downloads / 'results.json').write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    table = io.StringIO(newline='')
    writer = csv.writer(table)
    writer.writerow(['dataset', 'as_of', 'model', 'task', 'score', 'scored_runs', 'wall_ms', 'cost_usd', 'task_hash', 'receipt'])
    for m, entry in d['models'].items():
        for tid, c in entry['cells'].items():
            row = [d['version'], d['asof'], m, tid, c['score'], c['n'], c['wall'], c['cost'], c['hash'], c['receipt']]
            writer.writerow(["'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@', '\t', '\r')) else v for v in row])
    (downloads / 'results.csv').write_text(table.getvalue(), encoding='utf-8-sig')
    td = report.collect_task_data(runs)
    stories = []
    story_dir = out / 'stories'
    story_dir.mkdir(exist_ok=True)
    for story in STORIES:
        tid = story['task']
        if tid not in tdefs or tid not in td:
            continue
        cases = story_cases(td[tid], tdefs[tid], report._RUNS_BASE)
        if not cases:
            continue
        stories.append(story)
        hashes = set()
        artifact_dir = out / 'assets' / 'artifacts'
        artifact_dir.mkdir(parents=True, exist_ok=True)
        for case in cases:
            case['story_failure'] = case['score'] < 1 and any(check in '\n'.join(case['failures']) for check in story['checks'].split(', '))
            if case['app']:
                if report._PUBLIC_NAV:
                    from .boundary import _scrub
                    case['app'] = _scrub(case['app'].encode('utf-8'))[0].decode('utf-8')
                hashes.update(preview_hashes(case['app']))
                digest = hashlib.sha256(case['app'].encode()).hexdigest()
                (artifact_dir / (digest + '.txt')).write_text(case['app'], encoding='utf-8')
                case['app'] = '../assets/artifacts/' + digest + '.txt'
        nested = dict(common, nav=report._nav('../'), brand=report._brand('../'))
        write(story_dir / (story['id'] + '.html'), report._compiled(report._asset('story.html')).render(
            **nested, story=story, cases_json=json_for_script(cases), title=story['title'], preview_hashes=' '.join(sorted(hashes))))
    write(out / 'stories.html', report._compiled(report._asset('stories.html')).render(**common, stories=stories))
    import itertools
    import html
    complete = [(m, fmean(c['score'] for c in entry['cells'].values()))
                for m, entry in d['models'].items()
                if len(entry['cells']) == len(tdefs) and all(c['score'] is not None for c in entry['cells'].values())]
    leaders = [m for m, score in sorted(complete, key=lambda x: (-x[1], x[0]))[:3]]
    if len(leaders) > 1:
        comparison = report.build_compare_page(runs, tdefs, label, key)
        for a, b in itertools.combinations(leaders, 2):
            title = model_name(a) + ' vs ' + model_name(b)
            page = comparison.replace('<title>Compare · LLM Testing</title>', '<title>' + html.escape(title) + ' · Token Waster</title>')
            page = page.replace('</head>', '<meta name="comparison-a" content="' + html.escape(a, quote=True) + '"><meta name="comparison-b" content="' + html.escape(b, quote=True) + '"></head>', 1)
            write(out / f'compare--{report._slug_name(a)}--{report._slug_name(b)}.html', page)


def paired_inputs(runs, tdefs):
    return dataset(runs, tdefs)


def sharing_footer(source: str, version: str, asof: str, prefix: str) -> str:
    """Small citation disclosure on every report, evaluated from the current URL."""
    from . import report
    import html
    if '</body>' not in source:
        return source
    footer = ('<details class="report-citation" style="margin:24px 0"><summary>Cite or download this result</summary>'
              '<p>Every scored run per model and task contributes to the mean. The linked evidence records the tested conditions.</p>'
              '<textarea id="result-citation" readonly aria-label="Result citation" style="width:100%;min-height:90px"></textarea>'
              '<div class="actions"><button type="button" id="copy-citation">Copy citation</button> '
              '<button type="button" id="save-card">Download share image</button> '
              f'<a href="{prefix}downloads/results.csv">Dataset CSV</a> '
              f'<a href="{prefix}downloads/results.json">Dataset JSON</a></div>'
              '<p id="citation-status" role="status"></p></details>')
    meta = (f'<meta name="evidence-version" content="{html.escape(version, quote=True)}">'
            f'<meta name="evidence-asof" content="{html.escape(asof[:10], quote=True)}">')
    script = report._asset('sharing.html').replace('__VERSION__', json_for_script(version)).replace('__ASOF__', json_for_script(asof[:10]))
    return source.replace('</head>', meta + '</head>', 1).replace('</body>', footer + script + '</body>', 1)


def pin_evidence(root: Path, revision: str) -> int:
    """Bind all report receipts to a committed public snapshot, never private HEAD."""
    from .security import secure_report
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('expected a public commit hash')
    pattern = re.compile(r'(https://github\.com/tokenwaster/llm-testing-public/(?:tree|blob)/)(?:main|[0-9a-f]{40})(/(?:runs|archive|special|tasks|tasks-refs)(?:/|["\s]))')
    changed = 0
    for path in (root / 'reports').rglob('*'):
        if not path.is_file() or path.suffix not in {'.html', '.json', '.csv'}:
            continue
        source = path.read_text(encoding='utf-8-sig')
        pinned = pattern.sub(lambda m: m[1] + revision + m[2], source)
        if path.suffix == '.html':
            pinned = re.sub(r'<meta name="evidence-commit"[^>]*>', '', pinned)
            pinned = pinned.replace('</head>', f'<meta name="evidence-commit" content="{revision}"></head>', 1)
            pinned = secure_report(pinned)
        elif path.name == 'results.json':
            payload = json.loads(pinned)
            payload['evidence_commit'] = revision
            pinned = json.dumps(payload, ensure_ascii=False, indent=2)
        if pinned != source:
            path.write_text(pinned, encoding='utf-8-sig' if path.suffix == '.csv' else 'utf-8')
            changed += 1
    return changed
