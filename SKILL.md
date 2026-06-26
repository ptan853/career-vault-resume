---
name: career-timeline
description: Use when the user asks about their professional background, career history, identity, experiences, projects, skills, portfolio material, interview stories, or agent-readable user context; also use when resume work needs verified timeline facts before drafting.
---

# Career Timeline

Use this skill to maintain a local, portable professional timeline and identity
memory that agents can share across sessions. The vault stores profile details,
source material, career events, reusable claims, evidence, and generated
agent identity context. Resume support is limited to downstream handoff context and legacy/debug exports;
resume writing, tailoring, visual design, and PDF production belong in a separate
resume-designer skill.

Trigger this skill implicitly for questions about the user's background,
experience, career profile, projects, skills, professional identity, portfolio material, interview preparation, or
agent-readable background context. If the user asks for resume/CV/JD tailoring,
use this skill only to verify or complete the timeline, then hand off to a
resume-designer workflow for drafting and export. The
user does not need to name the skill.

This is a skill-guided workflow with a small deterministic CLI. The agent is
responsible for reading messy sources, extracting facts, asking review
questions, and deciding what is safe to use. The CLI is responsible for local
file operations such as initializing a vault, storing sources, adding events,
listing events, and generating identity or handoff exports. It does
not perform final resume writing, tailoring, visual design, or PDF rendering.

## Core Rules

- Treat the vault as the user's professional source of truth.
- Never invent employers, dates, metrics, awards, degrees, or responsibilities.
- Preserve raw source material before extracting events.
- Write AI output as draft events, draft claims, or patch previews unless the
  user explicitly confirms the information.
- Prefer confirmed event claims when generating agent identity summaries or
  downstream handoff context.
- Mark uncertain fields as `needs_review` instead of forcing a value.
- Keep stored facts language-neutral; localize only downstream generated artifacts.
- Store stable identity fields such as name, email, phone, and current
  location in `profile.yaml`, not as timeline events.
- Store an optional profile photo/headshot path in `profile.yaml` only when the
  user provides one; do not require it for timeline readiness.
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
4. Present one review card per extracted event before storing it.
5. Import reviewed draft events in bulk, or add a single event directly.
6. Add concise event-level claims when the source supports them.
7. Build `exports/agent_identity.md` when an agent needs user background.
8. Build timeline handoff context only when a downstream tool needs verified
   facts.

Do not present this skill as a resume generator. The CLI still includes legacy
`build-resume-context` and `build-basic-resume` commands for compatibility and
diagnostics, but final resume writing, JD tailoring, template selection, visual
design, editable HTML, DOCX/PDF export, and per-application state belong in a
separate resume-designer skill that consumes this timeline.

## Agent-Guided Use

Guide the user through the process instead of asking them to edit YAML. Ask for
the smallest useful next input: an old resume, a project link, a rough story,
a profile field, or confirmation of uncertain event fields.

After extracting events, show visible draft information and confirmation choices
before writing to the timeline. The default review format is one event card per
event. Do not replace multiple extracted events with a one-paragraph summary.
Do not generate a review Markdown file for routine review; use inline event
cards unless the user asks for a file or the batch is too large for chat.

Each event card should include the event title, type, time span, role,
organization, location, status, visibility, evidence/source, uncertain fields,
details, claims, and clear user choices:

```text
Confirm this event / edit fields / mark needs_review / skip this event
```

For 1-5 events, show full cards inline. For 6-12 events, show compact cards
inline, still one card per event. For 13 or more events, show a batch overview
and the first 10 cards, then ask whether to continue with the next batch or
create an external review artifact.

For multi-event extraction, create a JSON draft shaped like
`examples/draft_events.json`. Use `status: draft` unless the user explicitly
confirms the event. After the user reviews the list, import the draft with
`import-events`. This keeps semantic extraction in the agent while making local
storage deterministic.

When the user asks for a resume, CV, JD match, or job application material, do
not draft the resume in this skill. First check whether the timeline has enough
verified profile and event facts for a downstream resume-designer workflow. If
profile basics such as display name, email, phone, or location are missing, ask
for only the missing fields. If relevant events are missing or still
`needs_review`, continue timeline intake and event confirmation before handoff.

Photo/headshot is optional profile data. Tell the user they may provide one for
downstream templates, but do not block timeline work on it and do not decide
resume photo usage here.

Legacy/basic resume exports are only fallback diagnostics. Do not treat
`build-basic-resume` output as a final application resume, and do not use it to
replace a resume-designer workflow.

Do not hard-code one universal section list. When the user asks what the agent knows about them, asks for user-specific
professional advice, or asks about their background, build or read
`exports/agent_identity.md` before answering. If the identity export is missing
or stale, regenerate it with `build-identity`.

## Session Capture

When a session produces career-relevant work, offer to save it as a draft event.
This applies to completed projects, open-source releases, research notes,
portfolio work, job-search preparation, interview preparation, and
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
to adjust ownership, dates, public visibility, or artifact wording.

## Data Model

Use these primary objects:

- `SourceMaterial`: raw text, file references, URLs, GitHub/project material,
  resume PDFs, job descriptions, notes, and project material.
- `CareerEvent`: timeline unit such as work, internship, project, education,
  award, publication, certification, scholarship, startup, milestone, or custom.
- `Claim`: reusable fact derived from one event. In the current CLI, claims
  are stored as strings inside each event.
- `Evidence`: source reference that supports a claim. In the current CLI,
  evidence is represented by event `sources`; standalone evidence records are a
  planned extension.
- `Handoff context`: selected timeline facts for downstream tools such as resume designers or interview-prep agents.

Events should be flexible. Do not force work -> project -> achievement nesting.
Use event relations such as `part_of`, `occurred_during`, `related_to`,
`led_to`, and `resulted_in` when hierarchy or linkage matters.

## Event Extraction Standard

When extracting from resumes, files, notes, or links, look for small, reusable
events. One internship may contain several project events, one project may
contain claims, and one award or paper should be its own event when useful for
future reuse.

Each event should include at least:

```yaml
title: Built Career Timeline Skill
type: project
time:
  start: 2025-05
  end: 2025-08
  precision: month
```

Use optional fields when supported by the source:

```yaml
description: Built a local-first career timeline workflow with AI-assisted content rewriting.
role: Creator
organization: null
location: Remote
tags: [AI, career, artifacts]
details:
  tech_stack: Python
  achievement: Designed a reusable career timeline pipeline.
claims:
  - Designed a local-first career timeline workflow.
sources:
  - sources/src_project_note.md
visibility: private
status: draft
```

## Scripts

Use `scripts/career_timeline.py` for deterministic file operations:

```bash
python scripts/career_timeline.py --vault ~/.career-vault init
python scripts/career_timeline.py --vault ~/.career-vault add-source --type note --title "Career note" --text "..."
python scripts/career_timeline.py --vault ~/.career-vault add-source --type agent_session --title "Built Career Timeline skill" --text "..."
python scripts/career_timeline.py --vault ~/.career-vault add-event --title "Built Career Timeline Skill" --type project --start 2025-05 --description "..."
python scripts/career_timeline.py --vault ~/.career-vault import-events --file examples/draft_events.json
python scripts/career_timeline.py --vault ~/.career-vault list-events
python scripts/career_timeline.py --vault ~/.career-vault profile show --json
python scripts/career_timeline.py --vault ~/.career-vault profile update --display-name "Pat Example" --email "pat@example.com" --phone "+1 555 0100" --location "San Francisco, CA" --photo-path path/to/headshot.jpg
python scripts/career_timeline.py --vault ~/.career-vault check-readiness --for resume
python scripts/career_timeline.py --vault ~/.career-vault build-identity
# Legacy/debug handoff exports only; use a resume-designer skill for final resumes.
python scripts/career_timeline.py --vault ~/.career-vault build-resume-context --jd path/to/jd.md
python scripts/career_timeline.py --vault ~/.career-vault build-basic-resume --language zh --pages 1 --include-photo
```

The script does not replace agent judgment. Use the script to create, list, and
export vault files after extracting structured content. Schema validation,
standalone claim storage, source metadata records, photo processing, final resume writing, and PDF rendering are out of scope for
this skill.

## References

- Read `references/vault-format.md` before creating or modifying vault files.
- Read `references/extraction-guide.md` before extracting events from messy
  resumes, notes, links, or project material.
- Read `references/resume-context.md` only when preparing legacy/debug handoff
  context for a downstream resume workflow.

## Output Expectations

When updating the vault, summarize:

- sources added
- events created or changed
- claims created or changed
- fields marked `needs_review`
- generated export paths

When preparing downstream handoff context, explain which timeline events/claims
were selected and which facts still need user confirmation.
