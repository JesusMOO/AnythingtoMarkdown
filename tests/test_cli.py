from sptool import __version__


def test_version_string_exists():
    assert isinstance(__version__, str)
    assert __version__
