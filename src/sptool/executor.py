from dataclasses import dataclass
import subprocess


@dataclass(frozen=True)
class ExecutionResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(command: list[str]) -> ExecutionResult:
    completed = subprocess.run(command, capture_output=True, text=True)
    return ExecutionResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
