from pathlib import Path

from sptool.paths import directory_output_path, single_file_output_path


def test_single_file_output_stays_next_to_source():
    actual = single_file_output_path(Path(r"C:\work\a\report.pdf"))
    assert actual == Path(r"C:\work\a\report.md")


def test_directory_output_uses_parent_of_input_dir():
    actual = directory_output_path(
        root=Path(r"C:\work\books"),
        source=Path(r"C:\work\books\sub\chapter1.pdf"),
    )
    assert actual == Path(r"C:\work\sub\chapter1.md")
