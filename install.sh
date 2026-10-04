#!/usr/bin/env bash
# m3m-explain installer — https://github.com/hydra8/m3m-explain
#
#   ./install.sh [--target claude|agents|all] [--with-video] [--dry-run] [--uninstall]
#   curl -fsSL https://raw.githubusercontent.com/hydra8/m3m-explain/main/install.sh | bash
#
# --target      claude = ~/.claude/skills (Claude Code), agents = ~/.agents/skills (Codex, Pi
#               and other agents), all = both. Default: every one of them that exists;
#               if none exists, ~/.claude/skills.
# --with-video  also install the HyperFrames skills (by HeyGen) used for the video level.
# --dry-run     print what would happen, change nothing.
# --uninstall   remove m3m-explain from the same folders (HyperFrames is left alone).
set -euo pipefail

NAME="m3m-explain"
ARCHIVE="${M3M_ARCHIVE:-https://github.com/hydra8/m3m-explain/archive/refs/heads/main.tar.gz}"
TARGET=""
WITH_VIDEO=0
DRY=0
UNINSTALL=0

say() { printf '%s\n' "$*"; }
warn() { printf 'warn: %s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }
run() {
  if [ "$DRY" -eq 1 ]; then say "would run: $*"; else "$@"; fi
}

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --with-video) WITH_VIDEO=1; shift ;;
    --dry-run) DRY=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,13p' "$0" 2>/dev/null || true; exit 0 ;;
    *) die "unknown option: $1" ;;
  esac
done

CLAUDE_DIR="$HOME/.claude/skills"
AGENTS_DIR="$HOME/.agents/skills"
case "$TARGET" in
  claude) DIRS=("$CLAUDE_DIR") ;;
  agents) DIRS=("$AGENTS_DIR") ;;
  all) DIRS=("$CLAUDE_DIR" "$AGENTS_DIR") ;;
  "")
    DIRS=()
    [ -d "$CLAUDE_DIR" ] && DIRS+=("$CLAUDE_DIR")
    [ -d "$AGENTS_DIR" ] && DIRS+=("$AGENTS_DIR")
    if [ ${#DIRS[@]} -eq 0 ]; then
      if [ "$UNINSTALL" -eq 1 ]; then DIRS=("$CLAUDE_DIR" "$AGENTS_DIR"); else DIRS=("$CLAUDE_DIR"); fi
    fi
    ;;
  *) die "--target must be claude, agents or all" ;;
esac

if [ "$UNINSTALL" -eq 1 ]; then
  for dir in "${DIRS[@]}"; do
    if [ -e "$dir/$NAME" ]; then run rm -rf "$dir/$NAME"; say "removed: $dir/$NAME"; fi
  done
  exit 0
fi

# Source: the clone this script lives in, or a downloaded archive (curl | bash).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || pwd)"
SRC="$SCRIPT_DIR/skills/$NAME"
TMP=""
cleanup() { if [ -n "$TMP" ]; then rm -rf "$TMP"; fi; }
trap cleanup EXIT
if [ ! -f "$SRC/SKILL.md" ]; then
  TMP="$(mktemp -d)"
  if [ -f "$ARCHIVE" ]; then
    tar -xzf "$ARCHIVE" -C "$TMP"
  else
    command -v curl >/dev/null || die "curl is required to download $ARCHIVE"
    curl -fsSL "$ARCHIVE" | tar -xz -C "$TMP"
  fi
  SRC="$(find "$TMP" -type d -path "*/skills/$NAME" | head -n 1)"
  [ -n "$SRC" ] && [ -f "$SRC/SKILL.md" ] || die "skills/$NAME not found in $ARCHIVE"
fi

for dir in "${DIRS[@]}"; do
  run mkdir -p "$dir"
  run rm -rf "$dir/$NAME"
  run cp -R "$SRC" "$dir/$NAME"
  say "installed: $dir/$NAME"
done

# Environment checks: warnings only, nothing is installed here.
command -v python3 >/dev/null || warn "python3 not found — page checks and text scoring will not run"
chrome_found=0
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" google-chrome google-chrome-stable chromium chromium-browser; do
  if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then chrome_found=1; break; fi
done
[ "$chrome_found" -eq 1 ] || warn "Chrome/Chromium not found — page screenshots will be skipped"

if [ "$WITH_VIDEO" -eq 1 ]; then
  if command -v node >/dev/null && node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)'; then :; else
    warn "Node.js 22+ is required for the video level"
  fi
  ffmpeg -hide_banner -version >/dev/null 2>&1 || warn "working ffmpeg not found — needed for the video level"
  ffprobe -hide_banner -version >/dev/null 2>&1 || warn "working ffprobe not found — needed for the video level"
  if command -v npx >/dev/null || [ "$DRY" -eq 1 ]; then
    run npx hyperframes skills update
    run npx hyperframes skills update faceless-explainer
  else
    warn "npx not found — install Node.js 22+, then run: npx hyperframes skills update && npx hyperframes skills update faceless-explainer"
  fi
fi

say "done. Ask your agent: \"explain how a hash map works\" or call /$NAME"
