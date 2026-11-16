#!/usr/bin/env bash
# Symlink mỗi thư mục skill trong repo vào ~/.claude/skills/
set -euo pipefail
repo="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$dest"
for d in "$repo"/*/; do
  [ -f "$d/SKILL.md" ] || continue
  name="$(basename "$d")"
  target="$dest/$name"
  if [ -L "$target" ]; then ln -sfn "${d%/}" "$target"; echo "updated  $name"
  elif [ -e "$target" ]; then echo "skip     $name (đã có thư mục thật ở $target)"
  else ln -s "${d%/}" "$target"; echo "linked   $name"; fi
done
