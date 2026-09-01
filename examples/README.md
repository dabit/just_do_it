# Examples

## `claude-project-settings.json`

Merge this into a repository's `.claude/settings.json` and commit it, and everyone who clones that
repo gets JDI in Claude Code with nothing to install.

It is exactly what `claude plugin marketplace add dabit/just_do_it --scope project` followed by
`claude plugin install jdi@just-do-it --scope project` writes, so either route gets you the same
file — the CLI is easier, this is here for when you are merging into settings that already exist.

Change `repo` if you forked JDI.

**Use the `github` source, not a local path, for anything you commit.** The CLI absolutizes a
directory source — `--scope project` on `~/git/just_do_it` or even `./vendor/jdi` records
`/home/you/...`, which resolves on your machine and nowhere else. A committed `github` source
resolves for everyone.
