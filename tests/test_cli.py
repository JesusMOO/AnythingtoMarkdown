import runpy
import time
from types import SimpleNamespace
from pathlib import Path

import pytest

from sptool import __version__
from sptool.cli import main
import sptool.executor as executor


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
    class FakePopen:
        def __init__(self, command):
            self.command = command

        def wait(self):
            return 0

    monkeypatch.setattr("sptool.executor.subprocess.Popen", FakePopen)
    result = executor.run_command(["markitdown", "a.docx", "-o", "a.md"])
    assert result.returncode == 0


def test_start_command_returns_started_process(monkeypatch):
    class FakePopen:
        def __init__(self, command):
            self.command = command

    monkeypatch.setattr("sptool.executor.subprocess.Popen", FakePopen)
    started = executor.start_command(["markitdown", "a.docx", "-o", "a.md"])
    assert started.command == ["markitdown", "a.docx", "-o", "a.md"]
    assert started.process.command == ["markitdown", "a.docx", "-o", "a.md"]


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


class FakeProcess:
    def __init__(self, command, returncode=0, polls_to_finish=0):
        self.command = command
        self.returncode = returncode
        self.stdout = ""
        self.stderr = ""
        self._polls_remaining = polls_to_finish
        self._done = polls_to_finish == 0

    def poll(self):
        if self._done:
            return self.returncode
        if self._polls_remaining > 0:
            self._polls_remaining -= 1
        if self._polls_remaining == 0:
            self._done = True
            return self.returncode
        return None

    def wait(self, timeout=None):
        self._done = True
        return self.returncode


def test_directory_processing_launches_an_additional_job_when_resources_are_low(monkeypatch, tmp_path):
    root = tmp_path / "batch"
    root.mkdir()
    (root / "a.pdf").write_text("a", encoding="utf-8")
    (root / "b.pdf").write_text("b", encoding="utf-8")

    launched = []
    active = []
    overlap_detected = {"value": False}

    def fake_sample_resources():
        return SimpleNamespace(cpu=0.05, memory=0.05)

    def fake_start_command(command):
        if any(process.poll() is None for process in active):
            overlap_detected["value"] = True
        launched.append(command)
        process = FakeProcess(command, polls_to_finish=2)
        active.append(process)
        return process

    def fake_run_command(command):
        return FakeProcess(command)

    monkeypatch.setattr("sptool.cli.marker_initialization_required", lambda: False)
    monkeypatch.setattr("sptool.cli.sample_resources", fake_sample_resources, raising=False)
    monkeypatch.setattr("sptool.cli.start_command", fake_start_command, raising=False)
    monkeypatch.setattr("sptool.cli.run_command", fake_run_command)
    monkeypatch.setattr(time, "sleep", lambda *_args, **_kwargs: None)

    assert main([str(root)]) == 0
    assert len(launched) == 2
    assert overlap_detected["value"] is True


def test_directory_processing_stops_admitting_new_work_after_failure(monkeypatch, tmp_path):
    root = tmp_path / "batch"
    root.mkdir()
    (root / "a.pdf").write_text("a", encoding="utf-8")
    (root / "b.pdf").write_text("b", encoding="utf-8")
    (root / "c.pdf").write_text("c", encoding="utf-8")

    launched = []
    active = []

    def source_name(command):
        for part in command:
            text = str(part)
            if text.endswith(".pdf"):
                return Path(text).name
        return None

    def fake_sample_resources():
        return SimpleNamespace(cpu=0.05, memory=0.05)

    def fake_start_command(command):
        launched.append(command)
        returncode = 1 if source_name(command) == "b.pdf" else 0
        process = FakeProcess(command, returncode=returncode, polls_to_finish=2)
        active.append(process)
        return process

    def fake_run_command(command):
        return FakeProcess(command)

    monkeypatch.setattr("sptool.cli.marker_initialization_required", lambda: False)
    monkeypatch.setattr("sptool.cli.sample_resources", fake_sample_resources, raising=False)
    monkeypatch.setattr("sptool.cli.start_command", fake_start_command, raising=False)
    monkeypatch.setattr("sptool.cli.run_command", fake_run_command)
    monkeypatch.setattr(time, "sleep", lambda *_args, **_kwargs: None)

    assert main([str(root)]) == 5
    launched_sources = [source_name(command) for command in launched]
    assert "b.pdf" in launched_sources
    assert "c.pdf" not in launched_sources


def test_module_entrypoint_prints_banner_and_version(capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "exit")
    monkeypatch.setattr("sys.argv", ["sptool"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("sptool.cli", run_name="__main__")
    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "██████" in output
    assert "sptool v0.1.0" in output
