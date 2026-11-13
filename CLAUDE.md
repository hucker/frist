# frist: Claude Code instructions

@CODESTYLE.md

## Project shape

- Pure-Python library in `src/frist` (setuptools, src layout).  The public API is `__all__` in `src/frist/__init__.py`: `Chrono`, `Age`, `Cal`, `Biz`, `BizPolicy`, the unit classes, `TimeLike`, `time_pair`, `to_datetime`.  `Inclusive` is exported from `frist.units`, not from the top level.
- `__version__` in `src/frist/__init__.py` must match `version` in `pyproject.toml`.
- One runtime dependency, `python-dateutil` (only `dateutil.rrule`, in `src/frist/units/_month.py`).  Supported Pythons: 3.11 to 3.15 (the tox envlist); the dev venv is 3.15 (`.python-version`).
- CLI: `frist <date> [<date>]`, also `python -m frist`.  `src/frist/__main__.py` is excluded from coverage.
- Docs: `README.md` is the reference (long), `README_SMALL.md` the five-minute quick start, `docs/parallel-test.md` covers pytest-xdist.
- The git remote is named `frist`, not `origin`: `git push frist <branch>`.

## Domain invariants (never break silently)

- Windows are half-open, `[start, end)`.  `between()` with `Inclusive` is the explicit escape hatch for other inclusivity.
- Civil time.  `Cal` and `Biz` answer in the wall clock of the inputs; naive datetimes are wall-clock readings; `Age` measures true elapsed time when both endpoints are instants (aware datetimes in one zone, POSIX timestamps, `now`).  DST rules come from `zoneinfo`, never from frist.  Holidays are precomputed in `BizPolicy`.
- `Age`, `Cal` and `Biz` never mutate the datetimes they are given.
- `Age.from_seconds` / `Age.from_timedelta` build bare durations anchored at 2000-01-01, never through `datetime.fromtimestamp`.
- `Age.PLURAL_UNITS` (the default: a unit is used only once two of it have elapsed), `Age.AGE_UNITS` and `Age.DURATION_UNITS` are public `(threshold, unit_name, getter)` tables; `format()` walks them in order.

## Tests are the specification

- The README records a lesson: an AI once added 1 to a test input so a buggy case would pass.  Never change an expected value or an input, delete a test, or skip one to get green.  If a test looks wrong, stop and say so.
- Golden values must be checkable by eye (14 days of February is 0.5 months); never recompute an expected value with production logic.
- A run with skips is amber, not green.  Always report the skip count ("355 passed, 2 skipped: not green").

## Branch hygiene

Never commit on `main`.  Branch first, before any edit, as `<kind>/<dashed-slug>`:

| Kind    | Use for                                |
| ------- | -------------------------------------- |
| `feat`  | New features                           |
| `bug`   | Bug fixes                              |
| `doc`   | README / docs / docstring-only changes |
| `test`  | Test-only changes                      |
| `chore` | Tooling, dependencies, build           |
| `ref`   | Refactors with no behavior change      |

Releases keep the existing `release/X.Y.Z` form.  Merge to `main` with `git merge --ff-only`, and only when Chuck approves.  Commit messages are Conventional Commits with a scope: `feat(Age): ...`, `chore(deps): ...`, `docs(README): ...`.

## Tooling: uv-first

- `uv sync` installs the dev group (pytest, pytest-cov, pytest-xdist, hypothesis, mypy, types-python-dateutil, ruff, ty).  Never `pip install`.
- ruff, ty and mypy are pinned there; run them as `uv run ruff ...`, `uv run ty ...`, `uv run mypy ...`, never `uvx`, which would pick a different version.
- uv warns on every run that `VIRTUAL_ENV` points elsewhere.  That warning is expected; do not "fix" it.

## Quality gates (must all pass before declaring work done)

| Check             | Command                      | Pass criterion                |
| ----------------- | ---------------------------- | ----------------------------- |
| Lint              | `uv run ruff check`          | `All checks passed!`          |
| Format            | `uv run ruff format --check` | `N files already formatted`   |
| Type check        | `uv run mypy src/frist`      | `Success: no issues found`    |
| IDE Problems pane | (visual)                     | Zero entries                  |

`ruff check` only reports; fixing is an explicit `uv run ruff check --fix`, and the editor fixes on save.  `.githooks/pre-commit` runs the first three gates on every commit and refuses the commit on any finding.  ruff 0.17 also formats the Python code blocks inside Markdown files, so README edits go through the format gate too.

## Development (once per clone)

```text
git config core.hooksPath .githooks
git config alias.fdiff '!git -c diff.ruff-format.textconv="sh scripts/format_textconv.sh" diff'
git config alias.fblame 'blame --ignore-revs-file .git-blame-ignore-revs'
```

- The tree was ruff-formatted in one commit on 2026-11-13, listed in `.git-blame-ignore-revs`; the commit before it is tagged `pre-format`.  `git fdiff <old> <new>` diffs Python files as ruff formats them, so a comparison across that commit, or against an older branch, shows real changes only.  `git fblame <file>` skips the formatting commit.
- Before every commit: `uv run ruff check --fix`, `uv run ruff format`, then the gates.  Never `# fmt: off`, `# fmt: skip`, `# noqa` sweeps or `ty --add-ignore`.

## Testing

- `uv run pytest`: full suite, coverage on through `addopts`.  Use before commit and merge.
- `uv run pytest -m smoke`: about 99 tests in under a second, for tight iteration.
- `uv run pytest -n auto`: parallel (see `docs/parallel-test.md`).
- `uv run pytest -c .pytest_no_cov.ini test/test_age.py`: a focused run without coverage (`-c` replaces the pyproject config, so name the paths).
- `tox`: the full suite on every supported Python.
- Tests live in `test/` (singular) with no `conftest.py`; shared helpers are in `test/utils.py`.  Files are named for the surface they cover: `test_age*`, `test_biz*` / `test_bizpolicy*`, `test_cal*`, `test_chrono*`, `test_unit_namespace_*`.  Markers: `smoke`, `hypothesis`.
- Coverage of `src/frist` is 100% and stays there.

## Public API stability

- New names are added to `__all__`; nothing is removed without a one-release `DeprecationWarning`.
- Keep `frist.__version__` exported.

## Release flow (as practiced)

1. Feature branch, fast-forward merge to `main`.
2. Bump `version` in `pyproject.toml` and `__version__` in `src/frist/__init__.py`, run `uv lock`, commit as `chore: update version to X.Y.Z in pyproject.toml and __init__.py`.
3. Branch `release/X.Y.Z` and tag `X.Y.Z` (no `v`).
4. `uv build` into `dist/`.
5. Publishing to PyPI is Chuck's step.  Ask before doing it.
6. README badges and test counts are refreshed at release, not on feature branches.

## Docs and prose

- Every claim in the README must be literally true at the commit that carries it.  Never oversell.
- Run `/humanizer` after editing `README.md`, `README_SMALL.md` or `docs/`.
- No em dashes; do not use "honest" or "prove" for things tests establish.

## Secrets

`.pypirc` in the repo root holds a live PyPI token (gitignored).  Never read, print, grep or copy it.  `.claude/settings.json` denies reading it; keep that rule.

## Known gaps (do not fix unasked)

Listed so a session does not fix them mid-task.  Remove an item when a branch resolves it.

- `ty check src test` reports 45 diagnostics: 40 `unused-type-ignore-comment` (the pragmas mypy needs), 5 `invalid-argument-type`, 2 `int`.  Reconcile with a `[tool.ty.rules]` setting or crcglot's dual pragma before gating on ty.
- No CI workflow, although the README coverage badge links to GitHub Actions.
- No CHANGELOG; release history lives in commit messages.
- Tags stop at `0.16.0`; 0.17 to 0.21 were released without tags.
- `.vscode/tasks.json` is two JSON objects concatenated, so it does not parse.
- The README Age table lists `working_days`, `fiscal_year`, `fiscal_quarter`, `biz_policy` and `set_times()`, none of which exist on `Age`.
- `CODESTYLE.md` has typos (`expedted`, `paramerized`, `assert actual_sum = expected_sum`) and an unclosed code fence near line 60.
- `.gitignore` line 1 starts with a space instead of `#`, so it is a harmless pattern rather than a comment.
