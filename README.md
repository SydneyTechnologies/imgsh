# ImgTool

Privacy-first local image utility for resize, convert, batch processing, and optional OCR.

## Install

```bash
poetry install
```

Optional extras:

```bash
poetry install --extras "gui"
poetry install --extras "ocr"
poetry install --all-extras
```

Install with `pipx` from a local checkout:

```bash
pipx install "/absolute/path/to/imgtool[gui,ocr]"
```

Notes:
- `pipx install <path>` only installs base dependencies unless extras are included in the path spec.
- OCR is pinned to a `textract` version compatible with modern `pipx` dependency parsing.

## Commands

```bash
poetry run imgtool resize input.jpg --width 1200 --fit contain
poetry run imgtool batch-resize ./images --width 1200 --recursive --out ./processed
poetry run imgtool convert input.png --format webp
poetry run imgtool extract-text input.jpg --engine textract --ocr-format txt
poetry run imgtool gui
```

Run help:

```bash
poetry run imgtool --help
poetry run imgtool resize --help
```
