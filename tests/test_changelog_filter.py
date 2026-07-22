"""The info page shows one dataset's changelog. A live v0.6 report must not
carry v0.5 / v0.4 history — that lives in the archived reports and is noise for
the end user. `_changelog_for_version` keeps the preamble + Unreleased + the
current major.minor sections only.
"""
import re

from harness.report import _changelog_for_version

_MD = """# Changelog

Preamble text that should always survive.

## Unreleased

## 0.6.13 — new lanes
body for 0.6.13

## 0.6.2 — baseline
body for 0.6.2

## 0.5.26 — an archived patch
body for 0.5.26

## 0.4.0 — ancient
body for 0.4.0
"""


def _headers(md):
    return re.findall(r"(?m)^##\s+(\S+)", md)


def test_live_keeps_only_current_minor():
    out = _changelog_for_version(_MD, "0.6.13")
    assert _headers(out) == ["Unreleased", "0.6.13", "0.6.2"]
    assert "0.5.26" not in out and "0.4.0" not in out
    assert "Preamble text" in out


def test_archived_report_keeps_its_own_minor():
    out = _changelog_for_version(_MD, "0.5")
    assert _headers(out) == ["Unreleased", "0.5.26"]
    assert "0.6.13" not in out


def test_bodies_travel_with_their_section():
    out = _changelog_for_version(_MD, "0.6.13")
    assert "body for 0.6.13" in out and "body for 0.6.2" in out
    assert "body for 0.5.26" not in out
