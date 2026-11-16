status: pending
# 19 — `reference/herdr.md`: app sends that meet a `done` agent

Depends on: 12, 14

## Why
Task 12's probe (`## Probe log (#37)`) observed that once an agent's turn ends its status is `done`, and `hc send --if idle` refuses it ("<t> is done, not idle"). `### H6 on the app` answers a worker's `needs_input` with `hc send <terminal> "<answer>" --if idle --wait --timeout 300`: a worker that stopped to ask has ended its turn, so that send is always refused, and the user's answer never reaches it. Amended D6 still holds: never type into a dialog (a dialog reports no status or `blocked`, never `done`).

## Description
TDD is on: test first, red on its own assertion, then the fix.

1. **Probe** (through the Appendix B guard, throwaway session and home, exactly as task 12; tiny agent spend): with a Claude agent whose turn has ended (`done`), record
   - whether `hc read`, `hc get` or `hc wait` on it moves it from `done` to `idle` ("seen");
   - whether `hc send --if working` / plain `hc send` (no `--if`) to a `done` agent types and starts a turn;
   - what `hc send` does to a `blocked` agent without `--force` (expected: refused, exit 9).
   Record the results under `## Probe log (#37)` as R6.
2. **Fix `### H6 on the app`** (and any other app send in `reference/herdr.md` that can meet a `done` agent — check H5's state table and H9's handoff) so that an answer reaches a worker whose turn ended, without ever typing into a dialog. Preferred, if R6 shows reading clears `done`: read it first (the Butler reads the worker before answering anyway), then `--if idle`. Otherwise: send only after `hc get <terminal> --json` shows `status` `idle` or `done` (never missing, never `blocked`), and say why the plain send is safe then. Pick the smallest rule R6 supports and state the evidence.
3. Add the H5 state-table note if `done` needs one.

## Files
- `reference/herdr.md`
- `tests/test_herdr_operations.py`
- `plans/36-herdr-app-support/PLAN.md` (R6 under `## Probe log (#37)` only)

## Verification
1. A new test in `tests/test_herdr_operations.py` pins the fixed H6 rule (the exact fragments the fix writes, including how `done` is handled); red on its own assertion before the edit (`python3 -m unittest discover -s tests -p 'test_herdr_operations.py' -v`), green after.
2. Existing `test_h6_app` still passes ("never `hc keys`", "never `hc send --force`", "never `hc interrupt`" kept).
3. `python3 -m unittest discover -s tests -v` passes.
4. Probe cleanup verified as in task 12 (user's `hc ls --json` count, `~/.local/state/herdr-core/`, `herdr session list`, real `git worktree list` unchanged; no throwaway home or `~/.claude.json` entry left).
