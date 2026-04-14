from sptool import __version__
from sptool.cli import main
from sptool.executor import run_command


def test_version_string_exists():
    assert isinstance(__version__, str)
    assert __version__


def test_no_args_returns_success():
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


def test_single_file_path_calls_backend(monkeypatch, tmp_path):
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

    monkeypatch.setattr("sptool.cli.run_command", fake_run)
    assert main([str(source)]) == 0
    assert seen["command"][0] == "marker_single"
