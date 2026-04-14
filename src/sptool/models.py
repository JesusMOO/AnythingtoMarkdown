from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConversionJob:
    source: Path
    output: Path
    backend: str
