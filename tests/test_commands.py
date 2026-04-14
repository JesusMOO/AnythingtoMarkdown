from pathlib import Path

from sptool.commands import build_normal_command


def test_marker_normal_command_uses_output_dir():
    command = build_normal_command(
        backend="marker",
        source=Path(r"C:\work\a.pdf"),
        output=Path(r"C:\work\a.md"),
        extra_args=[],
    )
    assert command == [
        "marker_single",
        r"C:\work\a.pdf",
        "--output_dir",
        r"C:\work",
        "--output_format",
        "markdown",
    ]


def test_markitdown_normal_command_uses_output_file():
    command = build_normal_command(
        backend="markitdown",
        source=Path(r"C:\work\a.docx"),
        output=Path(r"C:\work\a.md"),
        extra_args=[],
    )
    assert command == [
        "markitdown",
        r"C:\work\a.docx",
        "-o",
        r"C:\work\a.md",
    ]
