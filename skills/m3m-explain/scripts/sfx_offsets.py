#!/usr/bin/env python3
"""Put sound effects on events inside a frame.

`fetch-sfx` from faceless-explainer puts every sound at the start of its frame (`offset_s: 0`)
and keeps one cue per sound name. This script reads the `sfx_at` field of each frame in
STORYBOARD.md (seconds, comma-separated, in the order of the `sfx` field), gives a repeated
sound its own cue, and writes the offsets to `audio_meta.json`. Run it after `fetch-sfx`
and before `assemble-index`.

Usage:
  sfx_offsets.py --storyboard STORYBOARD.md --audio-meta audio_meta.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FRAME_RE = re.compile(r'^#{2,3}\s+(?:Frame|Beat|Scene)\s+(\d+)', re.M)
FIELD_RE = re.compile(r'^-[ \t]*(\w+):[ \t]*(.*?)[ \t]*$', re.M)


def _frames(storyboard: str) -> dict[int, dict[str, str]]:
    heads = list(FRAME_RE.finditer(storyboard))
    frames = {}
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(storyboard)
        frames[int(head.group(1))] = dict(FIELD_RE.findall(storyboard[head.end():end]))
    return frames


def _expand_repeats(meta: dict, number: int, names: list[str], cues: list[dict]) -> list[dict]:
    """fetch-sfx keeps one cue per sound name; give a repeated name its own cue."""
    by_name = {Path(c.get('file', '')).stem: c for c in cues}
    if len(names) <= len(cues) or not all(n in by_name for n in names):
        return cues
    seen: set[str] = set()
    expanded = []
    for name in names:
        expanded.append(dict(by_name[name]) if name in seen else by_name[name])
        seen.add(name)
    sfx = meta['sfx']
    at = next(i for i, c in enumerate(sfx) if c is cues[0])
    rest = [c for c in sfx if c.get('frame') != number]
    meta['sfx'] = rest[:at] + expanded + rest[at:]
    return expanded


def apply_offsets(storyboard: str, meta: dict) -> dict:
    for number, fields in _frames(storyboard).items():
        if 'sfx_at' not in fields:
            continue
        offsets = [float(x) for x in fields['sfx_at'].split(',') if x.strip()]
        cues = [c for c in meta.get('sfx', []) if c.get('frame') == number]
        names = [n.strip() for n in fields.get('sfx', '').split(',') if n.strip()]
        cues = _expand_repeats(meta, number, names, cues)
        if len(offsets) > len(cues):
            raise ValueError(f'frame {number}: sfx_at has {len(offsets)} values but there are {len(cues)} sounds')
        duration = float(fields.get('duration', 'inf').rstrip('s'))
        for cue, offset in zip(cues, offsets):
            if not 0 <= offset < duration:
                raise ValueError(f'frame {number}: offset {offset} s is outside the frame ({duration} s)')
            cue['offset_s'] = offset
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--storyboard', required=True)
    ap.add_argument('--audio-meta', required=True)
    args = ap.parse_args()
    meta_path = Path(args.audio_meta)
    try:
        meta = apply_offsets(Path(args.storyboard).read_text(encoding='utf-8'),
                             json.loads(meta_path.read_text(encoding='utf-8')))
    except ValueError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    moved = sum(1 for c in meta.get('sfx', []) if c.get('offset_s'))
    print(f'offsets written: {moved} sound(s) not at the frame start')
    return 0


if __name__ == '__main__':
    sys.exit(main())
