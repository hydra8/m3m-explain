#!/usr/bin/env python3
"""Check an explanation HTML page before you hand it over.

Static checks: external resources, FILL markers, encoding, size.
Screenshots: headless Chrome at 1280 and 390 px; with --steps also the first and last player step.

Usage:
  check_page.py PAGE [--max-kb 200] [--screenshots DIR] [--steps] [--json]
Exit code 1 means static issues. Screenshots are taken even when there are issues.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXTERNAL_PATTERNS = [
    (re.compile(r'\bsrc\s*=\s*["\']?https?://', re.I), 'external resource in src='),
    (re.compile(r'url\(\s*["\']?https?://', re.I), 'external resource in url('),
    (re.compile(r'<link\b[^>]*\bhref\s*=\s*["\']?https?://', re.I), 'external <link href>'),
]
CHARSET = re.compile(r'<meta\s+charset\s*=\s*["\']?utf-8', re.I)


def static_issues(html: str, size_bytes: int, max_kb: int = 200) -> list[str]:
    issues = []
    for pattern, label in EXTERNAL_PATTERNS:
        for match in pattern.finditer(html):
            issues.append(f'{label}: {html[match.start():match.start() + 60]!r}')
    fills = html.count('FILL')
    if fills:
        issues.append(f'FILL markers left: {fills}')
    if not CHARSET.search(html):
        issues.append('no <meta charset="utf-8">: non-ASCII text breaks when the file opens from disk')
    if size_bytes > max_kb * 1024:
        issues.append(f'size {size_bytes // 1024} KB is over {max_kb} KB')
    return issues


CHROME_NAMES = ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser')
CACHED_CHROME_NAMES = ('chrome', 'chrome-headless-shell', 'Google Chrome for Testing')


def _default_candidates(home: Path | None = None) -> list[str]:
    found = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    found += [p for p in (shutil.which(n) for n in CHROME_NAMES) if p]
    cache = (home or Path.home()) / '.cache/hyperframes/chrome'
    if cache.is_dir():
        found += sorted(str(p) for p in cache.rglob('*') if p.name in CACHED_CHROME_NAMES and p.is_file())
    return found


def find_chrome(candidates: list[str] | None = None) -> str | None:
    for path in candidates if candidates is not None else _default_candidates():
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def narrow_wrapper(page_uri: str) -> str:
    """Wrapper page: headless Chrome will not make a window narrower than 500 px, so 390 px goes through an iframe."""
    return ('<!doctype html><html><head><meta charset="utf-8"><style>body { margin: 0; background: #808080; } '
            'iframe { width: 390px; height: 2400px; border: 0; display: block; }</style></head>'
            f'<body><iframe src="{page_uri}"></iframe></body></html>')


OVERFLOW_PROBE = '''<!doctype html><html><head><meta charset="utf-8"><title>PENDING</title></head>
<body style="margin: 0"><iframe id="f" src="{uri}" style="width: 390px; height: 800px; border: 0"></iframe>
<script>
document.getElementById('f').addEventListener('load', function () {{
  try {{
    var d = this.contentDocument.documentElement;
    document.title = d.scrollWidth > d.clientWidth ? 'OVERFLOW' : 'FITS';
  }} catch (e) {{ document.title = 'UNKNOWN'; }}
}});
</script></body></html>'''


def narrow_overflow(page: Path, chrome: str) -> bool | None:
    """True: at 390 px the page scrolls sideways. None: the check could not run."""
    probe = page.resolve().parent / f'.{page.stem}-overflow-probe.html'
    probe.write_text(OVERFLOW_PROBE.format(uri=page.resolve().as_uri()), encoding='utf-8')
    try:
        dom = subprocess.run(
            [chrome, '--headless=new', '--disable-gpu', '--allow-file-access-from-files',
             '--virtual-time-budget=3000', '--dump-dom', probe.as_uri()],
            capture_output=True, text=True, timeout=60, check=False).stdout
    finally:
        probe.unlink()
    match = re.search(r'<title>(OVERFLOW|FITS)</title>', dom)
    return None if not match else match.group(1) == 'OVERFLOW'


def _shot(chrome: str, url: str, path: Path, width: int, hide_scrollbars: bool) -> None:
    cmd = [chrome, '--headless=new', '--disable-gpu', f'--window-size={width},2400', f'--screenshot={path}']
    if hide_scrollbars:
        cmd.append('--hide-scrollbars')
    subprocess.run(cmd + [url], capture_output=True, timeout=60, check=False)


def screenshots(page: Path, out_dir: Path, chrome: str, steps: bool = False) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    url = page.resolve().as_uri()
    wrapper = out_dir / '_narrow.html'
    wrapper.write_text(narrow_wrapper(url), encoding='utf-8')
    shots = [(url, out_dir / 'wide.png', 1280, True), (wrapper.resolve().as_uri(), out_dir / 'narrow.png', 500, False)]
    if steps:
        shots += [(url + '#step=1', out_dir / 'step-first.png', 1280, True),
                  (url + '#step=last', out_dir / 'step-last.png', 1280, True)]
    made = []
    for shot_url, path, width, hide in shots:
        _shot(chrome, shot_url, path, width, hide)
        if path.exists():
            made.append(path)
    wrapper.unlink()
    return made


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('page')
    ap.add_argument('--max-kb', type=int, default=200)
    ap.add_argument('--screenshots')
    ap.add_argument('--steps', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    page = Path(args.page)
    data = page.read_bytes()
    issues = static_issues(data.decode('utf-8', errors='replace'), len(data), args.max_kb)
    shots: list[str] = []
    note = ''
    if args.screenshots:
        chrome = find_chrome()
        if chrome:
            shots = [str(p) for p in screenshots(page, Path(args.screenshots), chrome, args.steps)]
            overflow = narrow_overflow(page, chrome)
            if overflow:
                issues.append('at 390 px the page scrolls sideways: find the wide element')
            elif overflow is None:
                note = 'could not check overflow at 390 px'
        else:
            note = 'Chrome not found, screenshots skipped'

    if args.json:
        print(json.dumps({'issues': issues, 'screenshots': shots, 'note': note}, ensure_ascii=False, indent=2))
    else:
        print('no issues' if not issues else '\n'.join(f'- {i}' for i in issues))
        for path in shots:
            print(f'screenshot: {path}')
        if note:
            print(note)
    return 1 if issues else 0


if __name__ == '__main__':
    sys.exit(main())
