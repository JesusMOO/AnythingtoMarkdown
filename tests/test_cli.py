from sptool import __version__
from sptool.cli import main


def test_version_string_exists():
    assert isinstance(__version__, str)
    assert __version__


def test_no_args_returns_success():
    assert main([]) == 0


def test_help_flag_returns_success():
    assert main(["--help"]) == 0


def test_version_flag_returns_success():
    assert main(["--version"]) == 0
