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
imgsh crop input.jpg --x 120 --y 80 --width 640 --height 400
imgsh batch-resize ./images --width 1200 --recursive --out ./processed
imgsh convert input.png --format webp
imgsh extract-text input.jpg --engine textract --ocr-format txt
imgsh gui
```

## Help

```bash
imgsh -h
imgsh resize -h
imgsh crop -h
```

## GUI Crop

- Open an image in `imgsh gui`.
- Enable **Crop**, then drag on the preview to create a selection.
- Fine-tune the crop using **Left X / Top Y / Width / Height** (in original image pixels).
- Click **Export** to apply crop (and optional resize settings).

## Build Distribution Artifacts

```bash
poetry check
rm -rf dist
poetry build
pipx run twine check dist/*
```

## Publish

```bash
# bump patch version, commit, and create tag (for example v0.1.1)
poetry run publish

# bump minor instead
poetry run publish --bump minor

# set an explicit version
poetry run publish --version 0.2.0

# push commit and tag to origin (triggers tag-based publish workflow)
poetry run publish --push
```

A GitHub Actions workflow is included at `.github/workflows/publish.yml`.
Set `PYPI_API_TOKEN` in repository secrets, then push a tag like `v0.1.1` to publish automatically.

## Notes

- OCR extra is pinned to `textract==1.6.3` for compatibility with current packaging tooling.
