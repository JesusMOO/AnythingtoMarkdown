# sptool

## Install

```text
pip install -e .
```

This installs `sptool` and its default runtime dependencies:

- `marker-pdf[full]`
- `markitdown[all]`

## License

This project is distributed under a GPL-compatible strategy because the default dependency set includes `marker-pdf[full]`, and `marker` is published under GPL-3.0.

Relevant upstream licenses:

- `markitdown`: MIT
- `marker`: GPL-3.0

## Normal mode

```text
sptool
sptool --help
sptool --version
sptool file.pdf
sptool folder
sptool folder out
```

## Ultra mode

```text
sptool ultra start
sptool report.pdf --output_dir out --output_format markdown
sptool notes.docx -o notes.md
sptool ultra exit
```
