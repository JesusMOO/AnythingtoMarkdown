import shlex
import sys
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


def _handle_args(args: list[str]) -> int:
    mode = get_mode()
    if args == ["--help"]:
        print(render_help(mode))
        return 0
    if args == ["--version"]:
        print(__version__)
        return 0

    if args[:2] == ["ultra", "start"] or args[:2] == ["ultra", "exit"]:
        print(".error use the shell wrapper for ultra mode control.")
        return 2

    if not args:
        print(".error missing input path")
        return 2

    input_path = Path(args[0])
    if not input_path.exists():
        print(f".error input not found: {input_path}")
        return 2

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
        try:
            backend = detect_backend(source)
        except ValueError as exc:
            print(f".error {exc}")
            return 3
        if mode == "normal" and should_skip_output(output):
            print(f".skip {output} already exists")
            continue
        command = (
            build_ultra_command(backend, source, native_args)
            if mode == "ultra"
            else build_normal_command(backend, source, output, [])
        )
        try:
            result = run_command(command)
        except FileNotFoundError as exc:
            missing = exc.filename or command[0]
            print(f".error executable not found: {missing}")
            return 4
        if result.returncode != 0:
            print(f".error {backend} failed for {source}")
            if result.stderr:
                print(result.stderr.strip())
            return 5
        if mode == "normal":
            print(f".success {source} -> {output}")
        else:
            print(f".success {source}")

    return 0


def _run_repl() -> int:
    print(render_banner())
    print(f"sptool v{__version__}")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            return 0

        if not line:
            continue
        if line == "exit":
            return 0
        if not line.startswith("sptool"):
            print(".error expected 'sptool ...' or 'exit'")
            continue

        try:
            parts = shlex.split(line, posix=False)
        except ValueError as exc:
            print(f".error {exc}")
            continue

        if parts == ["sptool"]:
            print(".error missing command after 'sptool'")
            continue

        _handle_args(parts[1:])


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return _run_repl()
    return _handle_args(args)


if __name__ == "__main__":
    raise SystemExit(main())
