# Career Timeline

![Career Timeline cover](assets/cover.png)

<p align="center">
  <em>路漫漫其修远兮，吾将上下而求索。</em><br>
  <sub>The road ahead is long and far; I will keep searching high and low.</sub>
</p>

Agents forget you between sessions.

Career Timeline gives local coding agents a durable, inspectable memory of your
professional identity: who you are, what you have built, where each fact came
from, and what has been confirmed. It is the identity and career-memory layer
that other agents can trust before writing resumes, preparing interviews,
building portfolios, or answering user-specific career questions.

It is not a visual resume designer and should not be the final resume-writing
surface. For polished, editable, design-forward resumes, pair it with a separate
resume-designer skill that consumes this vault.

## Why This Exists

Career information is usually scattered across old resumes, PDFs, notes,
project repos, links, and chat sessions. A new agent sees none of it, so it asks
the same questions again or guesses.

This skill keeps source material local, extracts small reusable career events
with agent judgment, asks the user to confirm them, and exports a compact
identity file that future agents can read.

## What It Does

- Stores profile basics such as name, email, phone, location, target roles, and
  an optional photo path.
- Preserves raw sources from resumes, notes, files, URLs, GitHub material, job
  descriptions, and agent sessions.
- Lets an agent extract career events, claims, and source references into a
  local vault after user review.
- Imports multi-event JSON drafts produced by an agent review workflow.
- Exports `agent_identity.md` so future agents can understand the user's
  professional background.
- Optionally exports legacy handoff context for downstream resume or interview
  tools.

Current limits: no automatic PDF parsing, no standalone claim database yet, no
visual resume templates, no automatic photo processing, and no PDF rendering.
Final resume strategy, wording, layout, editable HTML/DOCX, and PDF export
belong in a separate resume-designer skill.

## How It Works

```text
resumes / notes / links / sessions / project material
        |
        v
agent extracts reviewed career events
        |
        v
.career-vault/
        |
        +--> exports/agent_identity.md
        +--> exports/resume_context.md  # optional downstream handoff
```

The Python CLI performs deterministic file operations. The agent does the
semantic work: reading messy material, identifying events, marking uncertainty,
and asking the user what should be confirmed.

## Install

Clone or keep this repository locally, then install it as a Codex-discoverable
skill:

```bash
ln -s /Users/pt623/Documents/career-timeline \
  /Users/pt623/.codex/skills/career-timeline
```

The same `SKILL.md` can also be read by Claude Code, Gemini CLI, OpenCode, or
other local agents that can access files and run shell commands. The CLI uses
only the Python standard library and requires Python 3.10+.

## Quick Start

Initialize a vault:

```bash
python scripts/career_timeline.py --vault ~/.career-vault init
```

Add profile basics:

```bash
python scripts/career_timeline.py --vault ~/.career-vault profile update \
  --display-name "Pat Example" \
  --email "pat@example.com" \
  --phone "+1 555 0100" \
  --location "San Francisco, CA" \
  --target-role "AI Engineer"
```

Optional profile fields, such as a headshot path, can be added later when a
downstream template or portfolio output needs them.

Import agent-extracted draft events:

```bash
python scripts/career_timeline.py --vault ~/.career-vault import-events \
  --file examples/draft_events.json
```

Export agent-readable identity context:

```bash
python scripts/career_timeline.py --vault ~/.career-vault build-identity
```

The generated identity file lives at:

```text
~/.career-vault/exports/agent_identity.md
```

Run `python scripts/career_timeline.py --help` for the full CLI. The legacy
`build-resume-context` and `build-basic-resume` commands remain available for
compatibility and diagnostics, but they are not the recommended final resume
path.

## Vault Files

```text
.career-vault/
  profile.yaml              # identity basics, target roles, optional photo
  sources/                  # preserved source notes, files, URLs, sessions
  events/                   # career events as YAML plus JSON sidecars
  claims/                   # reserved for standalone claim storage
  resumes/                  # reserved for downstream generated artifacts
  exports/
    agent_identity.md       # compact context for future agents
    resume_context.md       # optional downstream handoff context
    basic_resume.json       # legacy diagnostic export
    basic_resume.md         # legacy diagnostic export
    basic_resume.html       # legacy diagnostic export
```

Files are human-readable by design. Users can inspect them, version them, move
them across machines, or later index the same source of truth into SQLite or a
vector store.

## Agent Workflow

1. Read `SKILL.md` when a task involves the user's background, experience,
   professional identity, portfolio, job search, or interview stories.
2. Save raw material first with `add-source`.
3. Extract small career events from the material.
4. Show one review card per draft event, with evidence and confirmation
   choices. Do not replace a batch with a summary.
5. Import reviewed events with `import-events`.
6. Run `build-identity` before answering user-specific professional background
   questions.
7. For resume-related work, stop after checking timeline readiness and handing
   verified facts to a downstream resume-designer workflow.

For multi-event extraction, use the format in:

```text
examples/draft_events.json
```

## Project Layout

```text
career-timeline/
  SKILL.md                         # agent-facing workflow
  scripts/career_timeline.py       # standard-library CLI
  references/
    vault-format.md
    extraction-guide.md
    resume-context.md              # legacy/downstream handoff notes
  schemas/
    career-event.schema.json
    source-material.schema.json
    claim.schema.json
    vault-profile.schema.json
  examples/
    draft_events.json
    sample_jd.md
    sample_vault/
  tests/
    test_career_timeline_cli.py
```

## Status

This is an early skill-first MVP. It currently covers local identity storage,
career event storage, draft event import, agent identity export, and legacy
handoff exports.

Planned next steps:

- schema-backed validation
- standalone claim and evidence storage
- stronger source ingestion
- better source metadata and provenance review
- companion resume-designer skill that verifies this vault before drafting
