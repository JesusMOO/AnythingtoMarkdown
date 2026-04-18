from pathlib import Path


def build_normal_command(backend: str, source: Path, output: Path, extra_args: list[str]) -> list[str]:
    if backend == "marker":
        return [
            "marker_single",
            str(source),
            "--output_dir",
            str(output.parent),
            "--output_format",
            "markdown",
            *extra_args,
        ]
    if backend == "markitdown":
        return [
            "markitdown",
            str(source),
            "-o",
            str(output),
            *extra_args,
        ]
    raise ValueError(f"Unknown backend: {backend}")
