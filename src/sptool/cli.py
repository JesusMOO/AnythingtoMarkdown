from dataclasses import dataclass
import shlex
import subprocess
import sys
import time
from pathlib import Path

from sptool import __version__
from sptool.banner import render_banner
from sptool.commands import build_normal_command, build_ultra_command
from sptool.executor import ExecutionResult, run_command, start_command
from sptool.helptext import render_help
from sptool.marker_init import ensure_marker_ready, marker_initialization_required
from sptool.modes import get_mode
from sptool.paths import directory_output_path, should_skip_output, single_file_output_path
from sptool.routing import detect_backend
from sptool.scanner import iter_files

LOW_WATER_THRESHOLD = 0.60
HIGH_WATER_THRESHOLD = 0.70
POLL_INTERVAL_SECONDS = 0.5
_CPU_PERCENT_PRIMED = False
MAX_CONCURRENT_JOBS = 2


class MarkerInitializationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ResourceSample:
    cpu: float
    memory: float


@dataclass(frozen=True)
class Job:
    source: Path
    output: Path | None


@dataclass(frozen=True)
class PreparedJob:
    source: Path
    output: Path | None
    backend: str
    command: list[str]


@dataclass(frozen=True)
class ActiveJob:
    job: PreparedJob
    command: list[str]
    process: subprocess.Popen | object


def sample_resources() -> ResourceSample:
    global _CPU_PERCENT_PRIMED

    try:
        import psutil
    except ImportError:
        return ResourceSample(cpu=0.0, memory=0.0)

    if not _CPU_PERCENT_PRIMED:
        _CPU_PERCENT_PRIMED = True
        return ResourceSample(
            cpu=psutil.cpu_percent(interval=0.1) / 100.0,
            memory=psutil.virtual_memory().percent / 100.0,
        )

    return ResourceSample(
        cpu=psutil.cpu_percent(interval=None) / 100.0,
        memory=psutil.virtual_memory().percent / 100.0,
    )


def max_concurrency(resources: ResourceSample) -> int:
    if resources.cpu >= HIGH_WATER_THRESHOLD or resources.memory >= HIGH_WATER_THRESHOLD:
        return 0
    if resources.cpu <= LOW_WATER_THRESHOLD and resources.memory <= LOW_WATER_THRESHOLD:
        return MAX_CONCURRENT_JOBS
    return 0


def _collect_jobs(input_path: Path, explicit_output: Path | None, native_args: list[str], mode: str) -> list[Job]:
    jobs: list[tuple[Path, Path | None]] = []
    if input_path.is_file():
        output = explicit_output or single_file_output_path(input_path)
        jobs.append((input_path, output))
    else:
        for source in iter_files(input_path):
            jobs.append((source, directory_output_path(input_path, source)))

    return [Job(source=source, output=output) for source, output in jobs]


def _prepare_job(job: Job, native_args: list[str], mode: str) -> PreparedJob | None:
    backend = detect_backend(job.source)
    if mode == "normal" and job.output is not None and should_skip_output(job.output):
        print(f".skip {job.output} already exists")
        return None
    if backend == "marker" and marker_initialization_required():
        print(".info initializing marker models...")
        try:
            ensure_marker_ready()
        except Exception as exc:
            raise MarkerInitializationError(str(exc)) from exc
    command = (
        build_ultra_command(backend, job.source, native_args)
        if mode == "ultra"
        else build_normal_command(backend, job.source, job.output, [])
    )
    return PreparedJob(source=job.source, output=job.output, backend=backend, command=command)


def _success_marker(job: PreparedJob, mode: str) -> None:
    if mode == "normal" and job.output is not None:
        print(f".success {job.source} -> {job.output}")
    else:
        print(f".success {job.source}")


def _error_marker(job: PreparedJob, stderr: str) -> None:
    print(f".error {job.backend} failed for {job.source}")
    if stderr:
        print(stderr.strip())


def _coerce_started_process(started, command: list[str]) -> tuple[list[str], subprocess.Popen | object]:
    process = getattr(started, "process", started)
    actual_command = getattr(started, "command", command)
    return actual_command, process


def _finalize_process(process: subprocess.Popen | object, command: list[str]) -> ExecutionResult:
    if hasattr(process, "communicate"):
        stdout, stderr = process.communicate()
        returncode = process.wait()
        return ExecutionResult(
            command=command,
            returncode=returncode,
            stdout=stdout or "",
            stderr=stderr or "",
        )
    return ExecutionResult(
        command=command,
        returncode=getattr(process, "returncode", 0),
        stdout=getattr(process, "stdout", "") or "",
        stderr=getattr(process, "stderr", "") or "",
    )


def _run_jobs(jobs: list[Job], native_args: list[str], mode: str) -> int:
    if not jobs:
        return 0
    if len(jobs) == 1:
        job = _prepare_job(jobs[0], native_args, mode)
        if job is None:
            return 0
        try:
            result = run_command(job.command)
        except FileNotFoundError as exc:
            missing = exc.filename or job.command[0]
            print(f".error executable not found: {missing}")
            return 4
        if result.returncode != 0:
            _error_marker(job, result.stderr)
            return 5
        _success_marker(job, mode)
        return 0

    pending = list(jobs)
    running: list[ActiveJob] = []
    failed = False
    missing_executable: str | None = None
    deferred_exit_code: int | None = None
    deferred_error_message: str | None = None

    while pending or running:
        completed: list[ActiveJob] = []
        for active in running:
            if active.process.poll() is not None:
                completed.append(active)

        for active in completed:
            running.remove(active)
            result = _finalize_process(active.process, active.command)
            if result.returncode != 0:
                failed = True
                deferred_exit_code = None
                deferred_error_message = None
                _error_marker(active.job, result.stderr)
            else:
                _success_marker(active.job, mode)

        if failed:
            pending.clear()

        if missing_executable is not None:
            pending.clear()

        if deferred_exit_code is not None:
            pending.clear()

        if completed:
            if running:
                time.sleep(POLL_INTERVAL_SECONDS)
            continue

        if not running and pending and not failed:
            pending_job = pending.pop(0)
            try:
                job = _prepare_job(pending_job, native_args, mode)
            except ValueError as exc:
                print(f".error {exc}")
                return 3
            except MarkerInitializationError as exc:
                print(f".error marker initialization failed: {exc}")
                return 6
            if job is None:
                continue
            try:
                started = start_command(job.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except FileNotFoundError as exc:
                missing = exc.filename or job.command[0]
                if running:
                    missing_executable = missing
                    continue
                print(f".error executable not found: {missing}")
                return 4
            command, process = _coerce_started_process(started, job.command)
            running.append(ActiveJob(job=job, command=command, process=process))
        elif running and pending and not failed and missing_executable is None and deferred_exit_code is None:
            concurrency_limit = max_concurrency(sample_resources())
            if len(running) >= concurrency_limit:
                if running:
                    time.sleep(POLL_INTERVAL_SECONDS)
                continue
            pending_job = pending.pop(0)
            try:
                job = _prepare_job(pending_job, native_args, mode)
            except ValueError as exc:
                deferred_exit_code = 3
                deferred_error_message = f".error {exc}"
                continue
            except MarkerInitializationError as exc:
                deferred_exit_code = 6
                deferred_error_message = f".error marker initialization failed: {exc}"
                continue
            if job is None:
                continue
            try:
                started = start_command(job.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except FileNotFoundError as exc:
                missing = exc.filename or job.command[0]
                missing_executable = missing
                continue
            command, process = _coerce_started_process(started, job.command)
            running.append(ActiveJob(job=job, command=command, process=process))

        if running:
            time.sleep(POLL_INTERVAL_SECONDS)

    if missing_executable is not None:
        print(f".error executable not found: {missing_executable}")
        return 4
    if deferred_error_message is not None:
        print(deferred_error_message)
        return deferred_exit_code or 1
    return 5 if failed else 0


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

    try:
        jobs = _collect_jobs(input_path, explicit_output, native_args, mode)
    except ValueError as exc:
        print(f".error {exc}")
        return 3
    except MarkerInitializationError as exc:
        print(f".error marker initialization failed: {exc}")
        return 6

    try:
        return _run_jobs(jobs, native_args, mode)
    except ValueError as exc:
        print(f".error {exc}")
        return 3
    except MarkerInitializationError as exc:
        print(f".error marker initialization failed: {exc}")
        return 6


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
