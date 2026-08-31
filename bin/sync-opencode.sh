#!/usr/bin/env bash
# Sync JDI's commands and roles into OpenCode's global config.
#
# Claude Code and Codex both install this repository natively as a plugin
# (see README). OpenCode has no plugin loader, so its copy is synced here.
#
# - This repository is NEVER modified: it stays the single source of truth,
#   and `git pull` stays clean.
# - Command and agent files are namespaced `jdi-*` because OpenCode has no
#   plugin namespace — without the prefix, `next.md` would claim `/next`.
# - Re-run after every `git pull` in this repository.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OC="${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}"

if [ ! -d "$OC" ]; then
  echo "OpenCode config directory not found at $OC" >&2
  echo "Set OPENCODE_CONFIG_DIR to override." >&2
  exit 1
fi

mkdir -p "$OC/command" "$OC/agent"

python3 - "$SRC" "$OC" <<'PY'
import re, sys, pathlib

src, oc = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])

# OpenCode command frontmatter accepts only these keys; anything else fails
# validation. `argument-hint` is Claude-only and is dropped here.
COMMAND_KEYS = {"description", "agent", "model", "variant", "subtask"}

# OpenCode resolves models through its own provider config, and its `tools`
# schema differs from Claude's. Drop both and let OpenCode decide; JDI's tiers
# live in prose and in .jdi/config.yml, not in this frontmatter.
AGENT_DROP = {"model", "tools"}


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else (None, text)


def top_level_keys(fm_lines):
    """Yield (index, key) for lines that start a top-level YAML key.

    Continuation lines of a block scalar (description: |) are indented, so
    testing for a leading space is enough to keep multi-line values intact.
    """
    for i, line in enumerate(fm_lines):
        if line and not line[0].isspace():
            m = re.match(r"^([A-Za-z0-9_-]+)\s*:", line)
            if m:
                yield i, m.group(1)


def filter_frontmatter(fm, keep=None, drop=None):
    lines = fm.split("\n")
    keys = list(top_level_keys(lines))
    # Walk backwards so slicing does not shift the indices still to be handled.
    for pos, (i, key) in reversed(list(enumerate(keys))):
        end = keys[pos + 1][0] if pos + 1 < len(keys) else len(lines)
        unwanted = (keep is not None and key not in keep) or (
            drop is not None and key in drop
        )
        if unwanted:
            del lines[i:end]
    # Keep interior blank lines: they belong to multi-line block scalars, where
    # dropping them runs paragraphs of a description together.
    return "\n".join(lines).strip("\n")


def convert(text, *, keep=None, drop=None, rename=None, add_mode=False):
    # ${CLAUDE_PLUGIN_ROOT} only resolves inside Claude Code. Point OpenCode at
    # this checkout so reference/ and roles/ still resolve by path.
    text = text.replace("${CLAUDE_PLUGIN_ROOT}", str(src))
    fm, body = split_frontmatter(text)
    if fm is None:
        return text
    fm = filter_frontmatter(fm, keep=keep, drop=drop)
    if rename:
        fm = re.sub(r"^name:.*$", f"name: {rename}", fm, count=1, flags=re.M)
    if add_mode and not re.search(r"^mode:", fm, re.M):
        fm += "\nmode: subagent"
    return "---\n" + fm + "\n---\n" + body


n_cmd = n_agent = 0

for f in sorted((src / "commands").glob("*.md")):
    out = oc / "command" / f"jdi-{f.name}"
    out.write_text(convert(f.read_text(), keep=COMMAND_KEYS))
    n_cmd += 1

for f in sorted((src / "agents").glob("*.md")):
    name = f"jdi-{f.stem}"
    out = oc / "agent" / f"{name}.md"
    out.write_text(
        convert(f.read_text(), drop=AGENT_DROP, rename=name, add_mode=True)
    )
    n_agent += 1

print(f"Synced {n_cmd} commands -> {oc}/command/jdi-*.md")
print(f"Synced {n_agent} agents   -> {oc}/agent/jdi-*.md")
print(f"Reference files stay in {src} and are read from there.")
PY
