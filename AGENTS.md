# Repository Guidelines

## Project Structure & Module Organization

This repository defines a local-first professional timeline and identity memory skill with a supporting CLI. Core behavior lives in `scripts/career_timeline.py`, a standard-library Python command-line tool. Skill instructions are in `SKILL.md`; supporting documentation is in `references/`. JSON schemas for vault files live in `schemas/`. Visual assets live in `assets/`. Sample data and job-description inputs are in `examples/`, including `examples/sample_vault/`. Tests live in `tests/` and exercise the CLI end to end.

## Build, Test, and Development Commands

- `python scripts/career_timeline.py --help`: show CLI commands and options.
- `python scripts/career_timeline.py --vault /tmp/career-timeline init`: create a local vault for manual testing.
- `python scripts/career_timeline.py --vault /tmp/career-timeline add-event ...`: add a structured event; use `--help` on `add-event` for supported fields.
- `python -m pytest`: run the test suite configured in `pyproject.toml`.

The package targets Python 3.10+ and intentionally avoids runtime dependencies outside the Python standard library.

## Coding Style & Naming Conventions

Use clear, typed Python with `from __future__ import annotations` for new modules. Keep CLI functions small and named by command, for example `command_add_event`. Use snake_case for functions, variables, and filenames. Prefer `pathlib.Path` for filesystem work and UTF-8 for text I/O. Keep generated vault IDs aligned with existing prefixes such as `evt_...` and `src_...`.

## Testing Guidelines

Tests use `pytest` and should be placed in `tests/` with names like `test_<behavior>.py`. Prefer temporary vaults via `tmp_path` so tests do not touch a real `~/.career-vault`. Exercise CLI behavior through subprocesses when validating user-facing commands, as in `tests/test_career_timeline_cli.py`. Add regression tests for new commands, schema-affecting changes, and export formats.

## Commit & Pull Request Guidelines

Recent commits use short imperative subjects, such as `Add session capture workflow`. Follow that style: one concise line describing the change. Pull requests should include a summary, testing performed, and any schema or file-format compatibility notes. Include before/after examples when changing CLI output, generated Markdown, or vault file structure.

## Security & Configuration Tips

Career timelines may contain private resume and career data. Do not commit real user vaults, private source material, or generated exports unless explicitly intended. Use disposable paths such as `/tmp/career-timeline` for development and examples.
