from dataclasses import dataclass
import subprocess


@dataclass(frozen=True)
class StartedProcess:
    command: list[str]
    process: subprocess.Popen


@dataclass(frozen=True)
class ExecutionResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def start_command(command: list[str], **popen_kwargs) -> StartedProcess:
    return StartedProcess(command=command, process=subprocess.Popen(command, **popen_kwargs))


def run_command(command: list[str]) -> ExecutionResult:
    started = start_command(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = started.process.communicate()
    return ExecutionResult(
        command=started.command,
        returncode=started.process.wait(),
        stdout=stdout,
        stderr=stderr,
    )
