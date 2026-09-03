"""Shared helpers for JDI's test suite. Contains no tests of its own.

This repository is markdown all the way down, so everything the suite checks is a
file it reads as text: frontmatter delimiters, a fenced YAML schema block, a
markdown table, a hand-maintained list of file names. These helpers do the
reading, so each test module states an assertion rather than a parsing strategy.

`key_paths` is deliberately not a YAML parser. It handles the plain,
two-space-indented mapping subset that `reference/config.md`'s schema block and
`jdi.config.example.yml` are hand-written in, and it raises on anything outside
that subset — a tab, an odd indent — rather than silently misreading it. If the
configuration ever grows flow mappings or multi-line scalars, this fails loudly
and must grow with them.
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(relative_path):
    """Return the text of a file, given a path relative to the repository root."""
    return (ROOT / relative_path).read_text(encoding="utf-8")


def markdown_files(directory):
    """Every `*.md` in a directory, relative to the repository root, sorted."""
    return sorted(
        path.relative_to(ROOT).as_posix() for path in (ROOT / directory).glob("*.md")
    )


def command_slugs(directory="commands"):
    """Every `/jdi:<name>` slug derivable from a directory's `*.md` filenames.

    The filenames are the only source of truth for what commands exist — a
    harness registers `commands/done.md` as `/jdi:done` — so the slugs the
    documents are checked against are derived, never listed a third time.
    """
    return {
        "/jdi:" + pathlib.PurePosixPath(path).stem
        for path in markdown_files(directory)
    }


def split_frontmatter(text):
    """Split a command or role file into (frontmatter lines, body text).

    Returns `None` when the file has no well-formed `---` delimited frontmatter,
    which is what `bin/sync-opencode.sh`'s `convert()` splits on.
    """
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            return lines[1:index], "\n".join(lines[index + 1 :])
    return None


_KEY = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z0-9_.\-]+):(?: .*)?$")


def key_paths(lines):
    """Dotted key paths for a plain two-space-indented YAML mapping.

    Parent keys are emitted alongside their children, so `tracker:` yields
    `tracker` as well as `tracker.name`. Blank lines and comment lines are
    skipped — which is what makes a commented-out key in the example file
    genuinely absent rather than quietly counted.
    """
    paths = set()
    stack = []
    for number, line in enumerate(lines, start=1):
        if "\t" in line:
            raise ValueError(
                "line %d uses a tab; key_paths only reads two-space indentation: %r"
                % (number, line)
            )
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _KEY.match(line.rstrip())
        if not match:
            continue
        indent = len(match.group("indent"))
        if indent % 2:
            raise ValueError(
                "line %d is indented %d spaces; key_paths only reads two-space "
                "indentation: %r" % (number, indent, line)
            )
        depth = indent // 2
        if depth > len(stack):
            raise ValueError(
                "line %d jumps from depth %d to depth %d: %r"
                % (number, len(stack), depth, line)
            )
        del stack[depth:]
        stack.append(match.group("key"))
        paths.add(".".join(stack))
    return paths


def section(text, heading):
    """The lines under a markdown heading, up to the next heading of that level or above.

    Raises when the heading is absent, so a renamed section fails loudly instead
    of silently checking an empty list.
    """
    level = len(heading) - len(heading.lstrip("#"))
    lines = text.split("\n")
    try:
        start = lines.index(heading)
    except ValueError:
        raise AssertionError("heading %r not found" % heading)
    collected = []
    fenced = False
    for line in lines[start + 1 :]:
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and re.match(r"^#{1,%d} " % level, line):
            break
        collected.append(line)
    return collected


def paragraph_starting_with(text, prefix):
    """The paragraph whose first line starts with `prefix`, up to the next blank line."""
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            collected = []
            for candidate in lines[index:]:
                if not candidate.strip():
                    break
                collected.append(candidate)
            return collected
    raise AssertionError("no paragraph starting with %r found" % prefix)


def schema_block():
    """The YAML lines inside the first fenced block under `## Schema`.

    Scoped to that section on purpose: `## Example tier mappings` carries a
    second ```yaml fence whose three side-by-side `models:` columns would
    otherwise be read as schema keys.
    """
    lines = section(read("reference/config.md"), "## Schema")
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith("```"))
    except StopIteration:
        raise AssertionError("no fenced block under `## Schema` in reference/config.md")
    for offset, line in enumerate(lines[start + 1 :]):
        if line.startswith("```"):
            return lines[start + 1 : start + 1 + offset]
    raise AssertionError("unterminated fenced block under `## Schema` in reference/config.md")


def defaults_table_keys():
    """The backticked keys in the first column of the defaults table."""
    lines = section(read("reference/config.md"), "## Defaults when nothing is configured")
    keys = []
    for line in lines:
        match = re.match(r"^\| `([^`]+)` \|", line)
        if match:
            keys.append(match.group(1))
    if not keys:
        raise AssertionError("no rows found in reference/config.md's defaults table")
    return keys


def plugin_version():
    """The version in `.claude-plugin/plugin.json`."""
    return json.loads(read(".claude-plugin/plugin.json"))["version"]


def marketplace_version():
    """The version the marketplace records for the `jdi` plugin."""
    marketplace = json.loads(read(".claude-plugin/marketplace.json"))
    for plugin in marketplace["plugins"]:
        if plugin["name"] == "jdi":
            return plugin["version"]
    raise AssertionError("no plugin named `jdi` in .claude-plugin/marketplace.json")


def changelog_version():
    """The first `## <version>` heading in `CHANGELOG.md`."""
    match = re.search(r"^## (\S+)$", read("CHANGELOG.md"), re.MULTILINE)
    if not match:
        raise AssertionError("no `## <version>` heading found in CHANGELOG.md")
    return match.group(1)
