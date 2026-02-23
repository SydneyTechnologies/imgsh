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
pipx install "/absolute/path/to/imgtool[gui]"
pipx runpip imgtool install 'pip<24.1'
pipx runpip imgtool install 'textract==1.6.5'
```

Notes:
- `pipx install <path>` only installs base dependencies unless extras are included in the path spec.
- `textract` currently requires the `pip<24.1` workaround because of upstream dependency metadata.

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
