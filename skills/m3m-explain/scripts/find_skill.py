#!/usr/bin/env python3
"""Find the folder of an installed agent skill (for example, HyperFrames skills).

Search order: ~/.claude/skills, ~/.agents/skills, ~/.codex/skills, then Claude Code
plugin folders (~/.claude/plugins/**/skills/<name>, newest first). A folder counts only
if it contains SKILL.md.

Usage:
  find_skill.py <name>     prints the absolute path; exit 1 and "not found: <name>" otherwise
"""
from __future__ import annotations

import sys
from pathlib import Path

DIRECT = ('.claude/skills', '.agents/skills', '.codex/skills')


def find_skill(name: str, home: Path | None = None) -> Path | None:
    home = home or Path.home()
    for rel in DIRECT:
        folder = home / rel / name
        if (folder / 'SKILL.md').is_file():
            return folder
    plugins = home / '.claude/plugins'
    if plugins.is_dir():
        found = [p.parent for p in plugins.glob(f'**/skills/{name}/SKILL.md')]
        if found:
            return max(found, key=lambda p: (p / 'SKILL.md').stat().st_mtime)
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    folder = find_skill(sys.argv[1])
    if folder is None:
        print(f'not found: {sys.argv[1]}')
        return 1
    print(folder.resolve())
    return 0


if __name__ == '__main__':
    sys.exit(main())
