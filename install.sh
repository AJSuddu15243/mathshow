#!/usr/bin/env bash
# Installs mathshow for Claude Code: command on PATH, skill, and the two hooks.
#   ./install.sh              install
#   ./install.sh --uninstall  remove the symlinks and hooks
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin/mathshow"
SKILL="$HOME/.claude/skills/mathshow"
SETTINGS="$HOME/.claude/settings.json"

edit_hooks() {  # $1 = add|remove ; idempotent; keeps a one-time backup
  python3 - "$1" "$SETTINGS" "$BIN" <<'PY'
import json, os, shutil, sys
mode, path, cmd = sys.argv[1:]
cfg = json.load(open(path)) if os.path.exists(path) else {}
if os.path.exists(path) and not os.path.exists(path + ".bak-mathshow"): shutil.copy(path, path + ".bak-mathshow")
hooks = cfg.setdefault("hooks", {})
for event, arg in (("UserPromptSubmit", "clear"), ("Stop", "flush")):
    groups = [g for g in hooks.get(event, []) if not any("mathshow" in h.get("command", "") for h in g.get("hooks", []))]
    if mode == "add": groups.append({"hooks": [{"type": "command", "command": f'"{cmd}" {arg}'}]})
    if groups: hooks[event] = groups
    else: hooks.pop(event, None)
if not hooks: cfg.pop("hooks")
os.makedirs(os.path.dirname(path), exist_ok=True)
json.dump(cfg, open(path, "w"), indent=2); open(path, "a").write("\n")
PY
}

if [ "${1:-}" = "--uninstall" ]; then
  rm -f "$BIN"; rm -f "$SKILL"; edit_hooks remove
  echo "mathshow removed (settings backup, if any: $SETTINGS.bak-mathshow)"; exit 0
fi

missing=""
for c in node npm python3 magick; do command -v "$c" >/dev/null || missing="$missing $c"; done
if [ -n "$missing" ]; then
  echo "Missing:$missing"; echo "macOS: brew install node imagemagick   |   Debian/Ubuntu: apt install nodejs npm imagemagick python3"; exit 1
fi

(cd "$REPO" && npm install --omit=dev --no-audit --no-fund --silent)
mkdir -p "$(dirname "$BIN")" "$(dirname "$SKILL")"
ln -sf "$REPO/mathshow.py" "$BIN"; chmod +x "$REPO/mathshow.py"
ln -sfn "$REPO/skills/mathshow" "$SKILL"
edit_hooks add
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "Note: add $HOME/.local/bin to your PATH so the agent can run 'mathshow'." ;; esac
echo "Installed. Restart Claude Code, then ask for a derivation (Ghostty / Kitty-graphics terminal)."
