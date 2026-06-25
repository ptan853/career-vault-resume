---
name: career-vault-resume
description: Use when the user wants to create, update, or use a local career vault for resumes, CVs, project history, job applications, JD matching, interview stories, portfolio material, career events, or agent-readable professional identity.
---

# Career Vault Resume

Use this skill to maintain a local, portable career memory that agents can share.
The vault stores source material, career events, resume-safe claims, evidence,
and generated resume context. Prefer updating the vault before drafting resumes
or professional identity summaries.

Trigger this skill implicitly for resume, CV, career profile, project history,
job application, portfolio, interview preparation, or JD matching work. The user
does not need to name the skill.

This is a skill-guided workflow with a small deterministic CLI. The agent is
responsible for reading messy sources, extracting facts, asking review
questions, and deciding what is safe to use. The CLI is responsible for local
file operations such as initializing a vault, storing sources, adding events,
listing events, and generating basic exports. It does not currently perform
fully automatic resume parsing, claim validation, or PDF resume rendering.

## Core Rules

- Treat the vault as the user's professional source of truth.
- Never invent employers, dates, metrics, awards, degrees, or responsibilities.
- Preserve raw source material before extracting events.
- Write AI output as draft events, draft claims, or patch previews unless the
  user explicitly confirms the information.
- Prefer confirmed event claims when generating resumes or agent identity
  summaries.
- Mark uncertain fields as `needs_review` instead of forcing a value.
- Keep facts language-neutral; localize only generated resume text.
- Store resume header information such as name, email, phone, and current
  location in `profile.yaml`, not as timeline events.
- Do not include age by default. Ask before storing or showing age-related
  information.

## Vault Location

Default to the nearest `.career-vault/` directory. If none exists, use:

```text
~/.career-vault/
```

When working inside a project repo, ask before creating `.career-vault/` in that
repo unless the user explicitly wants the career memory versioned there.

## Workflow

1. Initialize or locate the vault.
2. Save user-provided material as a source.
3. Extract detailed career events from the source using agent judgment.
4. Present extracted events for user review before storing when practical.
5. Import reviewed draft events in bulk, or add a single event directly.
6. Add concise event-level claims when the source supports them.
7. Build `exports/agent_identity.md` when an agent needs user background.
8. Build `exports/resume_context.md` when a user provides a target JD.

Do not imply that this skill can already produce a final resume PDF. The current
resume output is `exports/resume_context.md`, which is source material for a
later resume drafting or rendering step.

## Agent-Guided Use

Guide the user through the process instead of asking them to edit YAML. Ask for
the smallest useful next input: an old resume, a project link, a rough story, a
JD, or confirmation of uncertain fields. After extracting events, show a concise
review list and ask the user what should be confirmed, edited, merged, hidden,
or left as `needs_review`.

For multi-event extraction, create a JSON draft shaped like
`examples/draft_events.json`. Use `status: draft` unless the user explicitly
confirms the event. After the user reviews the list, import the draft with
`import-events`. This keeps semantic extraction in the agent while making local
storage deterministic.

When the user asks for a resume, check whether `profile.yaml` has
`display_name`, `email`, `phone`, and `location`. If any are missing, ask for
only the missing fields before drafting the resume. If these values appear in a
source, treat them as suggestions and ask before writing them to the profile.
Age is optional and should remain excluded unless the user explicitly requests
it or the target resume context requires it.

## Session Capture

When a session produces career-relevant work, offer to save it as a draft event.
This applies to completed projects, open-source releases, research notes,
portfolio work, job-search preparation, resume generation, interviews, and
significant debugging or engineering work.

Use `agent_session` as the source type. The source should summarize what
happened in the session, not copy private conversation verbatim unless the user
asks for that. Create draft events from the session summary and include links to
repos, branches, commits, PRs, generated files, or published pages when known.

Ask before saving session-derived events. A good prompt is:

```text
This session produced career-relevant work. Should I save it to your career
vault as a draft event?
```

Session-derived events should usually start as `draft` because the user may want
to adjust ownership, dates, public visibility, or resume wording.

## Data Model

Use these primary objects:

- `SourceMaterial`: raw text, file references, URLs, GitHub/project material,
  resume PDFs, job descriptions, and notes.
- `CareerEvent`: timeline unit such as work, internship, project, education,
  award, publication, certification, scholarship, startup, milestone, or custom.
- `Claim`: resume-safe fact derived from one event. In the current CLI, claims
  are stored as strings inside each event.
- `Evidence`: source reference that supports a claim. In the current CLI,
  evidence is represented by event `sources`; standalone evidence records are a
  planned extension.
- `ResumeContext`: selected events and claims for a target job description.

Events should be flexible. Do not force work -> project -> achievement nesting.
Use event relations such as `part_of`, `occurred_during`, `related_to`,
`led_to`, and `resulted_in` when hierarchy or linkage matters.

## Event Extraction Standard

When extracting from resumes, files, notes, or links, look for small, reusable
events. One internship may contain several project events, one project may
contain claims, and one award or paper should be its own event when useful for
resume generation.

Each event should include at least:

```yaml
title: Built AI Resume Generator
type: project
time:
  start: 2025-05
  end: 2025-08
  precision: month
```

Use optional fields when supported by the source:

```yaml
description: Built a LaTeX-template resume generation workflow with AI-assisted content rewriting.
role: Creator
organization: null
location: Remote
tags: [AI, resume, LaTeX]
details:
  tech_stack: Python, LaTeX, FastAPI
  achievement: Designed a reusable resume generation pipeline.
claims:
  - Designed a template-driven resume generation workflow.
sources:
  - sources/resume_20260404.pdf
visibility: private
status: draft
```

## Scripts

Use `scripts/career_vault.py` for deterministic file operations:

```bash
python scripts/career_vault.py --vault ~/.career-vault init
python scripts/career_vault.py --vault ~/.career-vault add-source --type note --title "Career note" --text "..."
python scripts/career_vault.py --vault ~/.career-vault add-source --type agent_session --title "Built Career Vault Resume skill" --text "..."
python scripts/career_vault.py --vault ~/.career-vault add-event --title "Built AI Resume Generator" --type project --start 2025-05 --description "..."
python scripts/career_vault.py --vault ~/.career-vault import-events --file examples/draft_events.json
python scripts/career_vault.py --vault ~/.career-vault list-events
python scripts/career_vault.py --vault ~/.career-vault profile show --json
python scripts/career_vault.py --vault ~/.career-vault profile update --display-name "Pat Example" --email "pat@example.com" --phone "+1 555 0100" --location "San Francisco, CA"
python scripts/career_vault.py --vault ~/.career-vault check-readiness --for resume
python scripts/career_vault.py --vault ~/.career-vault build-identity
python scripts/career_vault.py --vault ~/.career-vault build-resume-context --jd path/to/jd.md
```

The script does not replace agent judgment. Use the script to create, list, and
export vault files after extracting structured content. Schema validation,
standalone claim storage, source metadata records, and resume PDF rendering are
not implemented yet.

## References

- Read `references/vault-format.md` before creating or modifying vault files.
- Read `references/extraction-guide.md` before extracting events from messy
  resumes, notes, links, or project material.
- Read `references/resume-context.md` before producing a targeted resume context
  from a JD.

## Output Expectations

When updating the vault, summarize:

- sources added
- events created or changed
- claims created or changed
- fields marked `needs_review`
- generated export paths

When generating resume context, explain which events/claims were selected and
which facts still need user confirmation.
