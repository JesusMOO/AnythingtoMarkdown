from sptool.modes import get_mode


def test_default_mode_is_normal(monkeypatch):
    monkeypatch.delenv("TOOL_MODE", raising=False)
    assert get_mode() == "normal"


def test_ultra_mode_from_env(monkeypatch):
    monkeypatch.setenv("TOOL_MODE", "ultra")
    assert get_mode() == "ultra"
