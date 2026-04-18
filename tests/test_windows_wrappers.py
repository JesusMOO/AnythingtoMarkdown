from pathlib import Path


def test_pyproject_installs_shell_wrappers_instead_of_console_script():
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    assert "[project.scripts]" not in text
    assert 'script-files = ["scripts/sptool.cmd", "scripts/sptool.ps1"]' in text


def test_cmd_wrapper_invokes_python_cli_without_repo_venv_path():
    text = Path("scripts/sptool.cmd").read_text(encoding="utf-8")
    assert ".venv" not in text
    assert '"%~dp0..\\python.exe" -m sptool.cli %*' in text
    assert 'if /I "%~1"=="ultra"' not in text


def test_powershell_wrapper_invokes_python_cli_without_repo_venv_path():
    text = Path("scripts/sptool.ps1").read_text(encoding="utf-8")
    assert ".venv" not in text
    assert '& "$PSScriptRoot\\..\\python.exe" -m sptool.cli @ArgsList' in text
    assert '$ArgsList[0] -eq "ultra"' not in text
