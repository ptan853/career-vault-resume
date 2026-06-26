# Career Vault Resume

![Career Vault Resume cover](assets/cover.png)

<p align="center">
  <em>路漫漫其修远兮，吾将上下而求索。</em><br>
  <sub>The road ahead is long and far; I will keep searching high and low.</sub>
</p>

Agents forget you between sessions.

Career Vault Resume gives local coding agents a durable, inspectable memory of
your professional identity: who you are, what you have built, where each fact
came from, and how that context should be reused for resumes, interviews,
portfolios, job applications, and future agent sessions.

It is not a visual resume designer. It is the identity and career-memory layer
that a resume generator, portfolio builder, or interview-prep agent can trust.
For polished, editable, design-forward resumes, install a separate resume
designer skill and use it together with this vault.

## Why This Exists

Most career information is scattered across old resumes, PDFs, notes, project
repos, links, job descriptions, and chat sessions. A new agent usually sees none
of it, so it either asks the same questions again or guesses.

This skill keeps the source material local, extracts small reusable career
events with agent judgment, and exports a compact identity file that future
agents can read before answering user-specific professional questions.

## What It Does

- Stores profile basics such as name, email, phone, location, target roles, and
  an optional photo path.
- Preserves raw sources from resumes, notes, files, URLs, GitHub material, job
  descriptions, and agent sessions.
- Lets an agent extract career events, claims, and source references into a
  local vault.
- Imports multi-event JSON drafts produced by an agent review workflow.
- Exports `agent_identity.md` so future agents can understand the user's
  professional background.
- Builds basic JD-specific `resume_context.md` for downstream resume drafting.
- Generates a conservative black-and-white basic resume as JSON, Markdown, and
  editable HTML.

Current limits: no automatic PDF parsing, no standalone claim database yet, no
visual resume templates, no automatic photo cropping, and no PDF rendering.
Complex, editable, designed resumes should be handled by a separate
resume-designer skill that consumes this vault's exported context.

## How It Works

```text
resumes / notes / links / sessions / JDs
        |
        v
agent extracts reviewed career events
        |
        v
.career-vault/
        |
        +--> exports/agent_identity.md
        +--> exports/resume_context.md
```

The Python CLI performs deterministic file operations. The agent does the
semantic work: reading messy material, identifying events, marking uncertainty,
and asking the user what should be confirmed.

## Install

Clone or keep this repository locally, then install it as a Codex-discoverable
skill:

```bash
ln -s /Users/pt623/Documents/career-vault-resume \
  /Users/pt623/.codex/skills/career-vault-resume
```

The same `SKILL.md` can also be read by Claude Code, Gemini CLI, OpenCode, or
other local agents that can access files and run shell commands. The CLI uses
only the Python standard library and requires Python 3.10+.

## Quick Start

Initialize a vault:

```bash
python scripts/career_vault.py --vault ~/.career-vault init
```

Add profile basics:

```bash
python scripts/career_vault.py --vault ~/.career-vault profile update \
  --display-name "Pat Example" \
  --email "pat@example.com" \
  --phone "+1 555 0100" \
  --location "San Francisco, CA" \
  --target-role "AI Engineer"
```

Optional profile fields, such as a headshot path, can be added later when a
template or portfolio output needs them.

Import agent-extracted draft events:

```bash
python scripts/career_vault.py --vault ~/.career-vault import-events \
  --file examples/draft_events.json
```

Export agent-readable identity context:

```bash
python scripts/career_vault.py --vault ~/.career-vault build-identity
```

The generated identity file lives at:

```text
~/.career-vault/exports/agent_identity.md
```

Generate a simple editable resume:

```bash
python scripts/career_vault.py --vault ~/.career-vault build-basic-resume \
  --language zh \
  --pages 1 \
  --include-photo
```

Run `python scripts/career_vault.py --help` for the full CLI. Use
`build-resume-context --jd jd.md` when a target job description is available.

## Vault Files

```text
.career-vault/
  profile.yaml              # identity basics, target roles, optional photo
  sources/                  # preserved source notes, files, URLs, sessions
  events/                   # career events as YAML plus JSON sidecars
  claims/                   # reserved for standalone claim storage
  resumes/                  # reserved for generated resume artifacts
  exports/
    agent_identity.md       # compact context for future agents
    resume_context.md       # JD-specific selected background
    basic_resume.json       # structured draft for simple resumes
    basic_resume.md         # readable black-and-white resume draft
    basic_resume.html       # editable browser version
```

Files are human-readable by design. Users can inspect them, version them, move
them across machines, or later index the same source of truth into SQLite or a
vector store.

## Agent Workflow

1. Read `SKILL.md` when a task involves the user's background, experience,
   professional identity, resume, portfolio, job search, or interview stories.
2. Save raw material first with `add-source`.
3. Extract small career events from the material.
4. Show one review card per draft event, with evidence and confirmation
   choices. Do not replace a batch with a summary.
5. Import reviewed events with `import-events`.
6. Run `build-identity` before answering user-specific professional background
   questions.
7. Run `build-resume-context` when a target JD is provided.

For multi-event extraction, use the format in:

```text
examples/draft_events.json
```

## Project Layout

```text
career-vault-resume/
  SKILL.md                         # agent-facing workflow
  scripts/career_vault.py          # standard-library CLI
  references/
    vault-format.md
    extraction-guide.md
    resume-context.md
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
    test_career_vault_cli.py
```

## Status

This is an early skill-first MVP. It currently covers local identity storage,
career event storage, draft event import, agent identity export, and basic
resume context/basic resume export.

Planned next steps:

- schema-backed validation
- standalone claim and evidence storage
- stronger source ingestion
- photo cropping and alignment for resume templates
- PDF export for the simple basic resume
- handoff to a separate resume-designer skill for polished editable HTML/PDF
  resumes
