# sptool | Markdown Everywhere

`sptool` is a compact CLI for converting many document types into Markdown through one consistent entrypoint.

It uses:

- [`marker`](https://github.com/datalab-to/marker) for PDF conversion
- [`markitdown`](https://github.com/microsoft/markitdown) for Office, web, data, archive, image, message, and audio formats

The goal is simple: keep the command surface small, keep the workflow predictable, and let `sptool` choose the right backend for the input file.

## Why sptool

- One command for multiple input formats
- Automatic backend selection by file extension
- Works with single files and folders
- Batch and folder conversions run concurrently by default
- Native backend arguments can be appended directly after the input path

## Supported formats

Handled by `marker`:

- `.pdf`

Handled by `markitdown`:

- `.docx`, `.pptx`, `.xlsx`, `.xls`
- `.html`, `.htm`, `.epub`
- `.csv`, `.json`, `.xml`, `.zip`
- `.msg`
- `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tiff`
- `.mp3`, `.wav`

## Install

```text
pip install -e .
```

On Windows, this installs shell wrappers instead of a Python console script so `sptool` resolves correctly in both `cmd` and PowerShell.

This installs `sptool` and its default runtime dependencies:

- `marker-pdf[full]`
- `markitdown[all]`

## Quick start

```text
sptool file.pdf
sptool notes.docx
sptool folder
sptool --help
```

`sptool` writes Markdown output automatically and skips files whose target `.md` already exists.

## Adaptive concurrency

When `sptool` processes multiple files, it starts work concurrently and keeps admitting new jobs while CPU and memory stay under the low-water threshold. If either resource rises above the high-water threshold, it stops starting new work until usage drops again.

Because multiple conversions can run at once, backend logs may interleave on stdout and stderr.

## CLI

```text
sptool
sptool --help
sptool --version
sptool file.pdf
sptool file.pdf out
sptool report.pdf --output_dir out --output_format markdown
sptool notes.docx -o notes.md
sptool folder
sptool folder out
```

## License

This project is distributed under a GPL-compatible strategy because the default dependency set includes `marker-pdf[full]`, and `marker` is published under GPL-3.0.

Relevant upstream licenses:

- `markitdown`: MIT
- `marker`: GPL-3.0
