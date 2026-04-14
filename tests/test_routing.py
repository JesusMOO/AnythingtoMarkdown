from pathlib import Path

from sptool.routing import detect_backend


def test_pdf_routes_to_marker():
    assert detect_backend(Path("a.pdf")) == "marker"


def test_docx_routes_to_markitdown():
    assert detect_backend(Path("a.docx")) == "markitdown"
