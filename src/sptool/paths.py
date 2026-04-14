from pathlib import Path


def single_file_output_path(source: Path) -> Path:
    return source.with_suffix(".md")


def directory_output_path(root: Path, source: Path) -> Path:
    relative = source.relative_to(root).with_suffix(".md")
    return root.parent / relative


def should_skip_output(output: Path) -> bool:
    return output.exists()
