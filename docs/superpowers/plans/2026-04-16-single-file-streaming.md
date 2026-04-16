# Single-File Streaming Logs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make direct single-file commands like `sptool file.pdf` stream backend logs in real time while keeping batch/directory execution unchanged.

**Architecture:** Add a dedicated streaming executor path in `src/sptool/executor.py` that lets the child process inherit the current console, and use it only from the single-file branch in `src/sptool/cli.py`. Keep adaptive batch scheduling on the existing captured-output path.

**Tech Stack:** Python 3.10+, `pytest`, standard-library `subprocess`

---

### Task 1: Lock In Single-File Streaming Behavior

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_single_file_path_uses_streaming_backend(monkeypatch, tmp_path, capsys):
    source = tmp_path / "a.pdf"
    source.write_text("x", encoding="utf-8")
    seen = {}

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr("sptool.cli.marker_initialization_required", lambda: False)
    monkeypatch.setattr("sptool.cli.run_command_streaming", lambda command: seen.setdefault("command", command) or Result(), raising=False)
    monkeypatch.setattr("sptool.cli.run_command", lambda command: (_ for _ in ()).throw(AssertionError("captured path should not be used")))

    assert main([str(source)]) == 0
    assert seen["command"][0] == "marker_single"


def test_directory_path_keeps_captured_batch_execution(monkeypatch, tmp_path):
    root = tmp_path / "batch"
    root.mkdir()
    (root / "a.pdf").write_text("x", encoding="utf-8")
    launched = []

    monkeypatch.setattr("sptool.cli.marker_initialization_required", lambda: False)
    monkeypatch.setattr("sptool.cli.sample_resources", lambda: SimpleNamespace(cpu=0.05, memory=0.05), raising=False)
    monkeypatch.setattr("sptool.cli.start_command", lambda command, **kwargs: launched.append(command) or FakeProcess(command), raising=False)
    monkeypatch.setattr("sptool.cli.run_command_streaming", lambda command: (_ for _ in ()).throw(AssertionError("streaming path should not be used")), raising=False)
    monkeypatch.setattr(time, "sleep", lambda *_args, **_kwargs: None)

    assert main([str(root)]) == 0
    assert launched
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `C:\Users\25963\AppData\Local\Programs\Python\Python310\Scripts\pytest.exe tests/test_cli.py -k "single_file_path_uses_streaming_backend or directory_path_keeps_captured_batch_execution" -q`
Expected: FAIL because `run_command_streaming` does not exist and the single-file path still uses `run_command`.

- [ ] **Step 3: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: define single-file streaming behavior"
```

### Task 2: Add Single-File Streaming Executor

**Files:**
- Modify: `src/sptool/executor.py`
- Modify: `src/sptool/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write minimal implementation**

```python
def run_command_streaming(command: list[str]) -> ExecutionResult:
    started = start_command(command)
    return ExecutionResult(
        command=started.command,
        returncode=started.process.wait(),
        stdout="",
        stderr="",
    )
```

And in the single-file branch in `src/sptool/cli.py`, call `run_command_streaming()` instead of `run_command()`.

- [ ] **Step 2: Run targeted tests**

Run: `C:\Users\25963\AppData\Local\Programs\Python\Python310\Scripts\pytest.exe tests/test_cli.py -k "single_file_path_uses_streaming_backend or directory_path_keeps_captured_batch_execution" -q`
Expected: PASS

- [ ] **Step 3: Run full suite**

Run: `C:\Users\25963\AppData\Local\Programs\Python\Python310\Scripts\pytest.exe -q`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/sptool/executor.py src/sptool/cli.py tests/test_cli.py
git commit -m "feat: stream logs for direct single-file runs"
```
