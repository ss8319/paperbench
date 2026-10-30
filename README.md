# Paperbench

A PDF editor that runs entirely in your browser. Merge, reorder, annotate, sign and compress PDFs without uploading them anywhere.

**Use it:** https://ss8319.github.io/paperbench · **Offline:** download [`dist/paperbench-offline.html`](dist/paperbench-offline.html) and double-click it. It works with no internet.

## What it does

| Area | Features |
|---|---|
| Pages | Open several PDFs and merge them · drag to reorder · rotate · delete · save only selected pages |
| Edit | Add and re-edit text · freehand drawing · highlight · whiteout · draw-and-place signature · insert PNG/JPEG · move and resize anything · undo |
| Compress | Three levels that keep text selectable, plus a Maximum level that flattens pages to images. Never saves a file bigger than the input |
| Privacy | All processing happens on your device. No server, no uploads, no account |

### Compression results

Measured with `npm run bench` on the generated test files in `tests/`. Sizes in KB.

| File | Original | Light (220 dpi) | Balanced (150 dpi) | Strong (96 dpi) | Maximum (flatten) |
|---|---:|---:|---:|---:|---:|
| Journal paper with figures | 4,502 | 351 | 150 | 79 | 1,975 |
| Phone-camera scan | 6,410 | 1,014 | 152 | 49 | 76 |
| PNG screenshots | 6,343 | 268 | 122 | 77 | 103 |
| Text only | 30 | 27 | 27 | 27 | 27 |
| 300 dpi office scan | 22,778 | 11,004 | 6,893 | 4,211 | 4,938 |

It works like Ghostscript and Smallpdf. It measures how large each image is drawn on the page, downsamples it to the target dpi, and re-encodes it as JPEG. It also compresses any uncompressed streams. Supported image types: JPEG (including CMYK), Flate/LZW with PNG predictors, indexed-colour, grayscale, 1–16 bit, and soft masks. JPEG 2000, JBIG2 and CCITT images are left untouched.

## Known limits

- **Whiteout is not redaction.** It covers content visually, but the text underneath is still in the file. Don't use it to hide confidential data.
- You can't edit the PDF's original text in place. Cover it with whiteout and type over it instead.
- Added text uses Helvetica and supports Latin characters only.
- No form filling, OCR, or password-protected PDFs yet.

See [ROADMAP.md](ROADMAP.md) for what's next.

## Development

The app is a single file: `src/paperbench.html`. It uses [pdf-lib](https://github.com/Hopding/pdf-lib) for writing PDFs and [pdf.js](https://github.com/mozilla/pdf.js) for rendering.

```bash
npm install
npm run build        # writes index.html (CDN libraries) and dist/paperbench-offline.html (libraries inlined)

pip install numpy pillow img2pdf reportlab matplotlib
python3 tests/make_test_pdfs_basic.py tests/pdfs
python3 tests/make_test_pdfs.py tests/pdfs
npm test             # end-to-end UI test in headless Chrome (add -- --offline for the offline build)
npm run bench        # compression table above
```

Tests use `playwright-core` with your installed Chrome. Set `CHROME=/path/to/chrome` if it isn't found.

## Licence

MIT. pdf-lib is MIT and pdf.js is Apache-2.0.
