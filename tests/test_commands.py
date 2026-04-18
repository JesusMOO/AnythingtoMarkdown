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


def test_marker_normal_command_preserves_native_args():
    command = build_normal_command("marker", Path("a.pdf"), Path("a.md"), ["--output_dir", "out"])
    assert command == ["marker_single", "a.pdf", "--output_dir", ".", "--output_format", "markdown", "--output_dir", "out"]


def test_markitdown_normal_command_preserves_native_args():
    command = build_normal_command("markitdown", Path("a.docx"), Path("a.md"), ["-o", "a.md"])
    assert command == ["markitdown", "a.docx", "-o", "a.md", "-o", "a.md"]
