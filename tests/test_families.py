from harness import report


def test_single_member_family_renders_a_full_card(monkeypatch):
    monkeypatch.setattr(report, "family_stats", lambda _runs, _tdefs: {
        "Solo": [{
            "model": "only-model",
            "score": 0.75,
            "coverage": 1.0,
            "local": False,
            "weights_gb": None,
            "vram_ref_gb": None,
            "quant": None,
            "tps": None,
        }]
    })
    monkeypatch.setattr(report, "_model_prefs", lambda: ({}, set()))
    monkeypatch.setattr(report, "_model_colors", lambda *_args: {})
    monkeypatch.setattr("harness.registry.load_families", lambda: {})

    page = report.build_family_page([], {})

    assert '<div class="famcard">' in page
    assert "Solo" in page
    assert "only-model" in page
    assert "Single-model families" not in page
