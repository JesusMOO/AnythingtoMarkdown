from pathlib import Path


MARKER_EXTENSIONS = {".pdf"}
MARKITDOWN_EXTENSIONS = {
    ".docx",
    ".pptx",
    ".xlsx",
    ".xls",
    ".html",
    ".htm",
    ".epub",
    ".csv",
    ".json",
    ".xml",
    ".zip",
    ".msg",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff",
    ".mp3",
    ".wav",
}


def detect_backend(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in MARKER_EXTENSIONS:
        return "marker"
    if suffix in MARKITDOWN_EXTENSIONS:
        return "markitdown"
    raise ValueError(f"Unsupported extension: {suffix}")
