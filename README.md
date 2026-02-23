# ImgTool

Privacy-first local image utility for resize, convert, batch processing, and optional OCR.

## Install

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e ".[gui]"
pip install -e ".[ocr]"
pip install -e ".[all]"
```

## Commands

```bash
imgtool resize input.jpg --width 1200 --fit contain
imgtool batch-resize ./images --width 1200 --recursive --out ./processed
imgtool convert input.png --format webp
imgtool extract-text input.jpg --engine textract --ocr-format txt
imgtool gui
```

Run help:

```bash
imgtool --help
imgtool resize --help
```
