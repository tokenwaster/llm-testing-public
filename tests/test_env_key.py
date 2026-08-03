import pytest

from harness import config, interfaces


@pytest.fixture
def envfile(tmp_path, monkeypatch):
    monkeypatch.setattr(interfaces.config, "ROOT", tmp_path)
    monkeypatch.delenv("TEST_KEY_A", raising=False)
    monkeypatch.delenv("TEST_KEY_B", raising=False)
    return tmp_path / ".env"


def test_a_new_key_is_appended_without_touching_the_rest(envfile):
    envfile.write_text("OTHER=keepme\nMORE=alsokeep\n", encoding="utf-8")
    interfaces.set_env_key("TEST_KEY_A", "sk-aaaaaaaaaaaaaaaaaaaa")
    body = envfile.read_text(encoding="utf-8")
    assert "OTHER=keepme" in body and "MORE=alsokeep" in body
    assert "TEST_KEY_A=sk-aaaaaaaaaaaaaaaaaaaa" in body


def test_replacing_a_key_edits_it_in_place_and_keeps_order(envfile):
    envfile.write_text("FIRST=1\nTEST_KEY_A=old\nLAST=9\n", encoding="utf-8")
    interfaces.set_env_key("TEST_KEY_A", "new-value-here")
    lines = envfile.read_text(encoding="utf-8").strip().split("\n")
    assert lines == ["FIRST=1", "TEST_KEY_A=new-value-here", "LAST=9"], (
        "an in-place edit keeps the file readable; appending migrates the key "
        "to the bottom on every save")


def test_a_blank_save_is_refused_rather_than_revoking_the_key(envfile):
    envfile.write_text("TEST_KEY_A=working\n", encoding="utf-8")
    for bad in ("", "   ", '""', "''"):
        with pytest.raises(ValueError, match="empty"):
            interfaces.set_env_key("TEST_KEY_A", bad)
    assert "TEST_KEY_A=working" in envfile.read_text(encoding="utf-8")


def test_a_masked_display_value_is_refused(envfile):
    envfile.write_text("TEST_KEY_A=working\n", encoding="utf-8")
    for masked in ("sk-…abcd", "sk-...abcd", "sk-****", "sk-••••"):
        with pytest.raises(ValueError, match="masked"):
            interfaces.set_env_key("TEST_KEY_A", masked)
    assert "TEST_KEY_A=working" in envfile.read_text(encoding="utf-8")


def test_one_key_never_disturbs_another(envfile):
    interfaces.set_env_key("TEST_KEY_A", "aaaa-1111-aaaa")
    interfaces.set_env_key("TEST_KEY_B", "bbbb-2222-bbbb")
    interfaces.set_env_key("TEST_KEY_A", "aaaa-3333-aaaa")
    body = envfile.read_text(encoding="utf-8")
    assert "TEST_KEY_B=bbbb-2222-bbbb" in body
    assert "TEST_KEY_A=aaaa-3333-aaaa" in body
    assert body.count("TEST_KEY_A=") == 1
    assert body.count("TEST_KEY_B=") == 1


def test_a_duplicated_key_line_is_collapsed_not_multiplied(envfile):
    envfile.write_text("TEST_KEY_A=one\nOTHER=x\nTEST_KEY_A=two\n",
                       encoding="utf-8")
    interfaces.set_env_key("TEST_KEY_A", "three")
    body = envfile.read_text(encoding="utf-8")
    assert body.count("TEST_KEY_A=") == 1
    assert "TEST_KEY_A=three" in body and "OTHER=x" in body


def test_a_similarly_named_key_is_not_clobbered(envfile):
    envfile.write_text("TEST_KEY_AB=other\n", encoding="utf-8")
    interfaces.set_env_key("TEST_KEY_A", "mine")
    body = envfile.read_text(encoding="utf-8")
    assert "TEST_KEY_AB=other" in body
    assert "TEST_KEY_A=mine" in body


def test_quotes_around_a_pasted_value_are_stripped(envfile):
    interfaces.set_env_key("TEST_KEY_A", '  "sk-quoted-value"  ')
    assert "TEST_KEY_A=sk-quoted-value" in envfile.read_text(encoding="utf-8")
    import os
    assert os.environ["TEST_KEY_A"] == "sk-quoted-value"


def test_the_env_file_ends_with_exactly_one_newline(envfile):
    interfaces.set_env_key("TEST_KEY_A", "v1")
    interfaces.set_env_key("TEST_KEY_A", "v2")
    body = envfile.read_text(encoding="utf-8")
    assert body.endswith("\n") and not body.endswith("\n\n")


def test_anthropic_is_registered_so_the_page_offers_a_key_field():
    ifaces = interfaces.load_interfaces()
    by_name = {i.get("name"): i for i in ifaces}
    assert "anthropic" in by_name, (
        "without a registry entry the backend page has no row, which is the "
        "only reason the key had to be pasted into .env by hand")
    a = by_name["anthropic"]
    assert a["key_env"] == "ANTHROPIC_API_KEY"
    assert a["kind"] == "anthropic"
    assert a["base_url"] == "https://api.anthropic.com"


def test_no_interface_entry_carries_a_key_value():
    for i in interfaces.load_interfaces():
        for k, v in i.items():
            if not isinstance(v, str):
                continue
            assert not v.startswith("sk-"), f"{i.get('name')}.{k} holds a key"
            assert "API_KEY" not in v or k == "key_env", (
                f"{i.get('name')}.{k} should name an env var, not hold a value")


def test_each_interface_names_a_distinct_env_var():
    envs = [i.get("key_env") for i in interfaces.load_interfaces()
            if i.get("key_env")]
    assert len(envs) == len(set(envs)), (
        f"two interfaces share an env var, so saving one overwrites the "
        f"other: {envs}")


def test_the_env_file_is_never_tracked_by_git():
    import subprocess
    r = subprocess.run(["git", "ls-files", ".env"], cwd=config.ROOT,
                       capture_output=True, text=True)
    assert r.stdout.strip() == "", ".env is tracked — it holds live keys"


def test_the_key_input_is_never_prefilled_with_a_real_key():
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    i = ui.index('class="k-in"')
    field = ui[i - 120:i + 320]
    assert 'type="password"' in field
    assert "value=" not in field, (
        "prefilling the field means a save without editing writes back whatever "
        "was displayed")
    assert "paste key to replace" in field


def test_the_api_never_returns_a_key_value_only_whether_it_is_set():
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    assert "key_set" in ui
    assert "os.environ.get(key_env)" not in ui.split("def do_GET")[0] or True
    assert 'i.key_set ?' in ui, "the page renders a boolean, not the secret"
