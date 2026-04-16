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


def start_command(command: list[str]) -> StartedProcess:
    return StartedProcess(command=command, process=subprocess.Popen(command))


def run_command(command: list[str]) -> ExecutionResult:
    started = start_command(command)
    return ExecutionResult(
        command=started.command,
        returncode=started.process.wait(),
        stdout="",
        stderr="",
    )
