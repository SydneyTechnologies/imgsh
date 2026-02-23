# Imgsh

Privacy-first local image utility for resize, convert, batch processing, and optional OCR.

## Install (Published Package)

```bash
pipx install "imgsh[gui,ocr]"
```

Or with `pip`:

```bash
pip install "imgsh[gui,ocr]"
```

## Install (Local Checkout with pipx)

```bash
pipx install "$HOME/Desktop/projects/imgsh[gui,ocr]"
```

`pipx install <path>` installs only base dependencies unless extras are included in the path spec.

## Development Setup

```bash
poetry install --all-extras
```

## Commands

```bash
imgsh resize input.jpg --width 1200 --fit contain
imgsh batch-resize ./images --width 1200 --recursive --out ./processed
imgsh convert input.png --format webp
imgsh extract-text input.jpg --engine textract --ocr-format txt
imgsh gui
```

## Help

```bash
imgsh -h
imgsh resize -h
```

## Build Distribution Artifacts

```bash
poetry check
rm -rf dist
poetry build
pipx run twine check dist/*
```

## Publish

```bash
# publish prebuilt artifacts in dist/
poetry publish

# or build and publish in one step
poetry publish --build
```

A GitHub Actions workflow is included at `.github/workflows/publish.yml`.
Set `PYPI_API_TOKEN` in repository secrets, then push a tag like `v0.1.1` to publish automatically.

## Notes

- OCR extra is pinned to `textract==1.6.3` for compatibility with current packaging tooling.
