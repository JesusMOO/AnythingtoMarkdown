# Marker Initialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically initialize Marker models the first time `sptool` converts a PDF, and fail fast with a clear error if initialization fails.

**Architecture:** Add a small `marker_init` helper module that lazily imports `surya` and performs a one-time predictor load before invoking `marker_single`. Integrate that helper into the PDF path in `cli.py`, keeping non-PDF behavior unchanged and surfacing initialization state and errors to the user.

**Tech Stack:** Python 3.10, pytest, marker-pdf/surya

---

### Task 1: Add regression tests for PDF initialization behavior

**Files:**
- Modify: `tests/test_cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_pdf_path_initializes_marker_before_running_backend(monkeypatch, tmp_path, capsys):
    ...

def test_pdf_initialization_failure_exits_without_running_backend(monkeypatch, tmp_path, capsys):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli.py -k marker -v`
Expected: FAIL because `main()` does not initialize marker models or stop on initialization failure yet.

- [ ] **Step 3: Write minimal implementation**

```python
if backend == "marker":
    ensure_marker_ready()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli.py -k marker -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/sptool/cli.py src/sptool/marker_init.py
git commit -m "feat: initialize marker models before pdf conversion"
```

### Task 2: Add lazy marker initialization helper

**Files:**
- Create: `src/sptool/marker_init.py`
- Modify: `src/sptool/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_pdf_initialization_failure_exits_without_running_backend(...):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli.py::test_pdf_initialization_failure_exits_without_running_backend -v`
Expected: FAIL with the backend command still being executed.

- [ ] **Step 3: Write minimal implementation**

```python
def ensure_marker_ready() -> None:
    from surya.models import load_predictors

    load_predictors()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli.py::test_pdf_initialization_failure_exits_without_running_backend -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/sptool/marker_init.py src/sptool/cli.py tests/test_cli.py
git commit -m "feat: fail fast when marker initialization fails"
```

### Task 3: Verify regression coverage

**Files:**
- Modify: `tests/test_cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the focused assertions**

```python
assert ".info initializing marker models..." in output
assert ".error marker initialization failed:" in output
```

- [ ] **Step 2: Run test to verify it fails if messaging regresses**

Run: `python -m pytest tests/test_cli.py -k marker -v`
Expected: FAIL if info or error messages are missing.

- [ ] **Step 3: Write minimal implementation**

```python
print(".info initializing marker models...")
print(f".error marker initialization failed: {exc}")
```

- [ ] **Step 4: Run targeted and full tests**

Run: `python -m pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/sptool/cli.py src/sptool/marker_init.py docs/superpowers/plans/2026-04-15-marker-initialization.md
git commit -m "test: cover marker initialization messaging"
```
