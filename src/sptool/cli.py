from pathlib import Path

from sptool import __version__
from sptool.banner import render_banner
from sptool.commands import build_normal_command, build_ultra_command
from sptool.executor import run_command
from sptool.helptext import render_help
from sptool.modes import get_mode
from sptool.paths import directory_output_path, should_skip_output, single_file_output_path
from sptool.routing import detect_backend
from sptool.scanner import iter_files


def main(argv=None) -> int:
    args = list(argv or [])
    mode = get_mode()
    if not args:
        print(render_banner())
        print(render_help(mode))
        return 0
    if args == ["--help"]:
        print(render_help(mode))
        return 0
    if args == ["--version"]:
        print(__version__)
        return 0

    if args[:2] == ["ultra", "start"] or args[:2] == ["ultra", "exit"]:
        print("Use the shell wrapper for ultra mode control.")
        return 2

    input_path = Path(args[0])
    explicit_output = Path(args[1]) if len(args) >= 2 and not args[1].startswith("-") else None
    native_args = args[2:] if explicit_output else args[1:]

    jobs = []
    if input_path.is_file():
        output = explicit_output or single_file_output_path(input_path)
        jobs.append((input_path, output))
    else:
        for source in iter_files(input_path):
            output = directory_output_path(input_path, source)
            jobs.append((source, output))

    for source, output in jobs:
        backend = detect_backend(source)
        if mode == "normal" and should_skip_output(output):
            print(f"[skip] {output} already exists")
            continue
        command = (
            build_ultra_command(backend, source, native_args)
            if mode == "ultra"
            else build_normal_command(backend, source, output, [])
        )
        result = run_command(command)
        if result.returncode != 0:
            return 5

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
