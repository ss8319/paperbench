"""Build Paperbench from src/paperbench.html.

Outputs:
  index.html                   loads pdf-lib and pdf.js from cdnjs (used by GitHub Pages)
  dist/paperbench-offline.html same app with both libraries inlined; works with no internet

Run `npm install` first so node_modules holds the pinned library versions.
"""
from pathlib import Path

ROOT = Path(__file__).parent
NM = ROOT / "node_modules"
CDN = "https://cdnjs.cloudflare.com/ajax/libs/"
LIBS = {
    f'<script src="{CDN}pdf-lib/1.17.1/pdf-lib.min.js"></script>': ("script", NM / "pdf-lib/dist/pdf-lib.min.js"),
    f'<script src="{CDN}pdf.js/3.11.174/pdf.min.js"></script>': ("script", NM / "pdfjs-dist/build/pdf.min.js"),
    f'<script src="{CDN}pdf.js/3.11.174/pdf.worker.min.js"></script>': ("worker", NM / "pdfjs-dist/build/pdf.worker.min.js"),
}


def wrap(fragment: str) -> str:
    """Turn the artifact fragment (title, style, markup, scripts) into a full HTML document."""
    i = fragment.index('<header class="bar">')
    head = fragment[:i].replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        f"{head}</head>\n<body>\n{fragment[i:]}\n</body>\n</html>\n"
    )


def inline(js: str) -> str:
    return js.replace("</script", "<\\/script").replace("<!--", "<\\!--")


def main():
    src = (ROOT / "src/paperbench.html").read_text()
    (ROOT / "index.html").write_text(wrap(src))
    offline = src
    for tag, (kind, path) in LIBS.items():
        assert offline.count(tag) == 1, f"missing script tag: {tag}"
        code = inline(path.read_text())
        repl = f"<script>{code}</script>" if kind == "script" else f'<script type="text/plain" id="pdfjs-worker-src">{code}</script>'
        offline = offline.replace(tag, repl)
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist/paperbench-offline.html").write_text(wrap(offline))
    for p in ["index.html", "dist/paperbench-offline.html"]:
        print(f"{p}: {(ROOT / p).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
