"""Markdown -> PNG long-image renderer.

Pipeline: pandoc (gfm -> html5) -> themed HTML template -> Playwright full-page screenshot.

Themes live in `references/themes/*.html` (next to this script's parent dir).
A theme is a full HTML document containing the markers `{{body}}` (required,
where pandoc output is injected) and `{{title}}` (optional, replaced by the
input filename stem).

Usage:
    python md2img.py INPUT.md [-o OUT.png] [--theme default]
                              [--width 390] [--scale 3]
                              [--channel msedge|chrome] [--no-html]

Deps:
    - pandoc (system)
    - playwright (pip) + `playwright install chromium` (or a --channel browser)
"""

import argparse
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
THEMES_DIR = SCRIPT_DIR.parent / "references" / "themes"

BODY_MARKER = "{{body}}"
TITLE_MARKER = "{{title}}"

# markers that pull in a sibling stylesheet at render time, so the emitted
# HTML stays self-contained (no relative <link> that breaks when the file is
# written elsewhere). name -> file under THEMES_DIR.
INCLUDE_MARKERS = {
    "{{callouts}}": "_callouts.css",
    "{{callouts-dark}}": "_callouts-dark.css",
}


def resolve_theme(theme_arg: str) -> pathlib.Path:
    """Resolve a theme name (or an explicit path) to an .html template file."""
    explicit = pathlib.Path(theme_arg)
    if explicit.is_file():
        return explicit
    if explicit.suffix:
        candidate = THEMES_DIR / explicit.name
    else:
        candidate = THEMES_DIR / f"{theme_arg}.html"
    if not candidate.is_file():
        available = ", ".join(sorted(t.stem for t in THEMES_DIR.glob("*.html"))) or "(none)"
        raise FileNotFoundError(
            f"theme '{theme_arg}' not found (looked in {THEMES_DIR}). available: {available}"
        )
    return candidate


def render(src: pathlib.Path, png: pathlib.Path, html: pathlib.Path,
           width: int, scale: int, channel, keep_html: bool,
           theme_path: pathlib.Path) -> None:
    # 1) pandoc md -> html fragment
    html_body = subprocess.run(
        ["pandoc", str(src), "-f", "gfm", "-t", "html5"],
        check=True, capture_output=True, text=True,
    ).stdout

    # 2) inject into themed template
    template = theme_path.read_text(encoding="utf-8")
    for marker, fname in INCLUDE_MARKERS.items():
        if marker in template:
            template = template.replace(
                marker, (THEMES_DIR / fname).read_text(encoding="utf-8"))
    if BODY_MARKER not in template:
        raise ValueError(
            f"theme {theme_path} is missing the required '{BODY_MARKER}' placeholder"
        )
    document = template.replace(TITLE_MARKER, src.stem).replace(BODY_MARKER, html_body)

    html.write_text(document, encoding="utf-8")
    print(f"[ok] {html} written (theme={theme_path.stem}, {len(html_body)} bytes body)")

    # 3) playwright full-page screenshot
    launch_kwargs = {}
    if channel:
        launch_kwargs["channel"] = channel
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(
            viewport={"width": width, "height": 844},
            device_scale_factor=scale,
        )
        page.goto(html.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(png), full_page=True)
        browser.close()

    print(f"[ok] {png} written ({png.stat().st_size} bytes)")

    if not keep_html:
        html.unlink(missing_ok=True)
        print(f"[ok] removed intermediate {html}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Markdown -> PNG long image (themed).")
    ap.add_argument("src", type=pathlib.Path, help="input markdown file")
    ap.add_argument("-o", "--output", type=pathlib.Path,
                    help="output PNG (default: <src>.png)")
    ap.add_argument("--html", type=pathlib.Path,
                    help="intermediate HTML path (default: <src>.html)")
    ap.add_argument("--theme", default="default",
                    help="theme name under references/themes/ or an .html path (default: default)")
    ap.add_argument("--width", type=int, default=390,
                    help="viewport width in px (default: 390)")
    ap.add_argument("--scale", type=int, default=3,
                    help="device scale factor (default: 3)")
    ap.add_argument("--channel", default=None,
                    help="browser channel e.g. msedge/chrome (default: bundled chromium)")
    ap.add_argument("--no-html", action="store_true",
                    help="delete intermediate HTML after rendering")
    args = ap.parse_args()

    if not args.src.is_file():
        print(f"[err] input not found: {args.src}", file=sys.stderr)
        return 1

    try:
        theme_path = resolve_theme(args.theme)
    except FileNotFoundError as e:
        print(f"[err] {e}", file=sys.stderr)
        return 2

    png = args.output or args.src.with_suffix(".png")
    html = args.html or args.src.with_suffix(".html")

    render(args.src, png, html, args.width, args.scale,
           args.channel, keep_html=not args.no_html, theme_path=theme_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
