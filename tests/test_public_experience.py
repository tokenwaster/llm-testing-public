import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from harness import boundary, experience, report, security, viewer


def test_final_byte_guard_catches_nested_credentials_and_links(tmp_path):
    artifact = tmp_path / 'reports' / 'generated.html'
    artifact.parent.mkdir()
    artifact.write_text('safe report', encoding='utf-8')
    boundary.guard_tree(tmp_path)
    credential = 'sk-' + 'aZ19' * 12
    artifact.write_text(credential, encoding='utf-8')
    with pytest.raises(RuntimeError) as error:
        boundary.guard_tree(tmp_path)
    assert 'generated.html' in str(error.value)
    assert credential not in str(error.value)
    cleaned, count = boundary._scrub(artifact.read_bytes())
    assert count == 1 and credential.encode() not in cleaned
    artifact.write_text('safe', encoding='utf-8')
    (artifact.parent / '.env.production').write_text('secret', encoding='utf-8')
    with pytest.raises(RuntimeError, match='private file'):
        boundary.guard_tree(tmp_path)


def test_nonpublished_bytecode_does_not_trigger_the_content_gate(tmp_path):
    cache = tmp_path / '__pycache__'
    cache.mkdir()
    (cache / 'fixture.pyc').write_bytes(('sk-' + 'aZ19' * 12).encode())
    boundary.guard_tree(tmp_path)


def test_generated_content_cannot_become_report_markup_or_raw_active_html():
    dangerous = '</script><img src=x onerror=alert(1)>'
    encoded = security.json_for_script({'name': dangerous})
    assert '<' not in encoded and json.loads(encoded)['name'] == dangerous
    assert viewer.Handler.CTYPES['.html'].startswith('text/plain')
    assert viewer.Handler.CTYPES['.svg'].startswith('text/plain')
    preview = security.isolated_preview('<script>window.x=1</script>')
    assert preview.index('Content-Security-Policy') < preview.index('<script>')
    assert "connect-src 'none'" in security.PREVIEW_CSP


def test_report_csp_is_based_on_final_script_bytes_and_is_idempotent():
    page = '<html><head></head><body><script>const x=1;</script></body></html>'
    secured = security.secure_report(page)
    assert security._hash('const x=1;').replace("'", '&#x27;') in secured
    assert security.secure_report(secured) == secured
    changed = security.secure_report(secured.replace('const x=1;', 'const x=2;'))
    assert security._hash('const x=2;').replace("'", '&#x27;') in changed
    assert security._hash('const x=1;').replace("'", '&#x27;') not in changed


def test_shortlist_data_preserves_missing_cost_and_conditions(monkeypatch):
    monkeypatch.setattr(report, '_model_prefs', lambda: ({}, set()))
    monkeypatch.setattr(report, '_is_subscription', lambda es: es[0]['model'].startswith('codex-cli'))
    td = SimpleNamespace(content_hash='h', title='A task', category='coding-python')
    def run(model, effort, budget):
        return {'run_id': model, 'manifest': {'suite_version': '0.7', 'finished': '2026-09-06',
                'mode': 'serial', 'model_sampling': {model: {'max_tokens': budget}}},
                'results': [{'model': model, 'task': 't', 'task_hash': 'h', 'category': 'coding-python',
                 'tier': 1, 'score': {'status': 'scored', 'score': 1}, 'sampling_used': {},
                 'effort_used': effort, 'cost_usd': None, 'wall_ms': 10, 'attempts': []}]}
    d = experience.dataset([run('api-model', None, 65536), run('codex-cli-model', 'inherited', 65536)], {'t': td})
    api = d['models']['api-model']['cells']['t']
    cli = d['models']['codex-cli-model']['cells']['t']
    assert api['cost'] is None and cli['cost'] is None
    assert api['n'] == 1 and api['condition']
    assert cli['condition'] is None
    assert 'CLI' in d['models']['codex-cli-model']['name']


def test_new_pages_are_accessible_and_do_not_fetch_artifacts_until_requested():
    choose = report._asset('choose.html')
    assert '<label>Your work<select' in choose and 'role="status"' in choose
    story = report._asset('story.html')
    assert "setAttribute('sandbox','allow-scripts')" in story
    assert "allow-same-origin" not in story
    assert "load.onclick=async()=>" in story
    assert "No individual failure detail was recorded" in story


def test_task_summary_is_not_a_subscription_price():
    assert 'API figures' in report.cost_note() and 'Missing prices are not free' in report.cost_note()
    assert 'Latest-per-model' not in report.TASK_TEMPLATE
    assert 'overlapping bands do not' in report.INFO_TEMPLATE


def test_pinning_uses_a_public_commit_and_rehashes_the_finished_page(tmp_path):
    folder = tmp_path / 'reports'
    folder.mkdir()
    receipt = 'https://github.com/tokenwaster/llm-testing-public/tree/main/runs/r/m/t'
    page = folder / 'model.html'
    page.write_text('<html><head></head><body><script>const url="' + receipt + '";</script></body></html>', encoding='utf-8')
    revision = 'a' * 40
    assert experience.pin_evidence(tmp_path, revision) == 1
    result = page.read_text(encoding='utf-8')
    assert '/tree/' + revision + '/runs/' in result and '/tree/main/' not in result
    assert 'evidence-commit' in result and 'data-report-csp' in result
    assert experience.pin_evidence(tmp_path, revision) == 0
    with pytest.raises(ValueError):
        experience.pin_evidence(tmp_path, 'main')


def test_viewer_preserves_a_published_snapshot(monkeypatch, tmp_path):
    (tmp_path / 'index.html').write_text('<meta name="evidence-commit" content="' + 'a' * 40 + '">', encoding='utf-8')
    monkeypatch.setattr(viewer.config, 'REPORTS_DIR', tmp_path)
    monkeypatch.setattr(viewer, 'QuietServer', lambda *args: SimpleNamespace(serve_forever=lambda: None))
    def unexpected(**kwargs):
        raise AssertionError('published citations must not be regenerated on startup')
    monkeypatch.setattr(viewer.report, 'generate_all', unexpected)
    viewer.serve(9001)

