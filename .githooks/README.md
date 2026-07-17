# Git hooks (opt-in)

Local pre-commit gates that mirror the enforced CI checks, giving you fast
feedback *before* a commit is written instead of after CI runs.

## What the pre-commit hook does

* **Encoding integrity** — scans staged files for double-encoded UTF-8
  (mojibake) via `scripts/lint/check_mojibake.py --staged` and blocks the
  commit if any is found.
* **Markdown lint** — runs `markdownlint-cli2 --fix` on staged `*.md`, re-stages
  the safe auto-fixes, then blocks if any residual lint errors remain.

Both checks are also enforced in CI (`.github/workflows/ci.yml`: `mojibake-scan`
and `markdown-lint`), so the hook is a convenience, not the source of truth.

## Enable it

Run once per clone:

```bash
git config core.hooksPath .githooks
```

## Requirements

* `python3` (or `python`) on `PATH` for the mojibake gate.
* `node`/`npx` on `PATH` for the markdown lint gate.

If a tool is missing the hook prints a warning and skips that gate — CI still
enforces it.

## Repairing mojibake

```bash
python scripts/lint/fix_mojibake.py <file>   # then: git add <file>
```

Lines that must display a literal mojibake example can carry a `mojibake-allow`
marker to suppress the check for that line.
