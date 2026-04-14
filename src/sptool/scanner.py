from pathlib import Path


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file():
            yield path
