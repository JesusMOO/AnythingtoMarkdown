import runpy

import pytest

from sptool import __version__
from sptool.cli import main
from sptool.executor import run_command


def test_version_string_exists():
    assert isinstance(__version__, str)
    assert __version__


def test_no_args_returns_success(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "exit")
    assert main([]) == 0


def test_help_flag_returns_success():
    assert main(["--help"]) == 0


def test_version_flag_returns_success():
    assert main(["--version"]) == 0


def test_run_command_returns_success_for_zero_exit(monkeypatch):
    class Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr("sptool.executor.subprocess.run", lambda *a, **k: Completed())
    result = run_command(["markitdown", "a.docx", "-o", "a.md"])
    assert result.returncode == 0


def test_single_file_path_calls_backend(monkeypatch, tmp_path, capsys):
    source = tmp_path / "a.pdf"
    source.write_text("x", encoding="utf-8")
    seen = {}

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command):
        seen["command"] = command
        return Result()

    monkeypatch.setattr("sptool.cli.marker_initialization_required", lambda: False)
    monkeypatch.setattr("sptool.cli.run_command", fake_run)
    assert main([str(source)]) == 0
    assert seen["command"][0] == "marker_single"
    assert ".success" in capsys.readouterr().out


def test_single_file_failure_prints_error(monkeypatch, tmp_path, capsys):
    source = tmp_path / "a.pdf"
    source.write_text("x", encoding="utf-8")

    class Result:
        returncode = 1
        stdout = ""
        stderr = "backend failed"

    monkeypatch.setattr("sptool.cli.marker_initialization_required", lambda: False)
    monkeypatch.setattr("sptool.cli.run_command", lambda command: Result())
    assert main([str(source)]) == 5
    assert ".error" in capsys.readouterr().out


def test_pdf_path_initializes_marker_before_running_backend(monkeypatch, tmp_path, capsys):
    source = tmp_path / "a.pdf"
    source.write_text("x", encoding="utf-8")
    events = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_init():
        events.append("init")

    def fake_run(command):
        events.append(command[0])
        return Result()

    monkeypatch.setattr("sptool.cli.ensure_marker_ready", fake_init, raising=False)
    monkeypatch.setattr("sptool.cli.run_command", fake_run)

    assert main([str(source)]) == 0

    output = capsys.readouterr().out
    assert ".info initializing marker models..." in output
    assert events == ["init", "marker_single"]


def test_pdf_initialization_failure_exits_without_running_backend(monkeypatch, tmp_path, capsys):
    source = tmp_path / "a.pdf"
    source.write_text("x", encoding="utf-8")
    seen = {"run": False}

    def fake_init():
        raise RuntimeError("network blocked")

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command):
        seen["run"] = True
        return Result()

    monkeypatch.setattr("sptool.cli.ensure_marker_ready", fake_init, raising=False)
    monkeypatch.setattr("sptool.cli.run_command", fake_run)

    assert main([str(source)]) == 6

    output = capsys.readouterr().out
    assert ".error marker initialization failed: network blocked" in output
    assert seen["run"] is False


def test_module_entrypoint_prints_banner_and_version(capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "exit")
    monkeypatch.setattr("sys.argv", ["sptool"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("sptool.cli", run_name="__main__")
    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "██████" in output
    assert "sptool v0.1.0" in output
