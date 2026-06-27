---
name: career-timeline
description: Use when the user asks about their professional background, career history, identity, experiences, projects, skills, portfolio material, interview stories, or agent-readable user context; also use when resume work needs verified timeline facts before drafting.
---

# Career Timeline

Maintain a local professional timeline and identity memory that agents can reuse
across sessions. The vault stores profile fields, raw sources, reviewed career
events, reusable claims, evidence links, and `exports/agent_identity.md`.

This is not a final resume writer. For resume/CV/JD requests, use this skill only
to verify timeline facts and readiness, then hand off to a separate
resume-designer workflow for strategy, writing, layout, editable output, and PDF
export.

## Core Rules

- Treat the vault as the user's professional source of truth.
- Preserve raw source material before extracting events.
- Never invent employers, dates, metrics, awards, degrees, or responsibilities.
- Store stable identity fields such as name, email, phone, and location in
  `profile.yaml`, not as timeline events.
- Store photo/headshot path only if the user provides one; never require it for
  timeline readiness.
- Do not include age by default. Ask before storing or showing age-related data.
- Write AI output as draft events, draft claims, or patch previews unless the
  user explicitly confirms it.
- Mark uncertain fields as `needs_review` instead of forcing a value.
- Keep stored facts language-neutral; localize only downstream artifacts.

## Vault Location

Default to the nearest `.career-vault/`. If none exists, use `~/.career-vault/`.
Ask before creating `.career-vault/` inside a project repo unless the user wants
career memory versioned there.

## Workflow

1. Locate or initialize the vault.
2. Save user-provided material as a source.
3. Extract detailed career events using agent judgment.
4. Show one review card per extracted event before storing it.
5. Import reviewed draft events in bulk, or add one confirmed event directly.
6. Add concise event-level claims when the source supports them.
7. Build `exports/agent_identity.md` before answering user-specific background
   questions.
8. For resume-related work, stop after timeline readiness/handoff; do not draft
   the final resume here.

## Event Detail Standard

A useful event must preserve enough material for later tailoring. Extract more
than a title and generic description when the source supports it. Aim to capture:

- `context`: situation, problem, goal, audience, or why the work mattered.
- `contribution`: what the user personally did, owned, led, or supported.
- `implementation`: methods, technologies, architecture, data, tools, or tradeoffs.
- `outcome`: shipped artifact, metric, business result, research result, release,
  benchmark, report, or other evidence-backed result.
- `evidence`: source file, URL, repo, commit, PR, certificate, report, or user
  confirmation supporting the event.
- `claims`: concise reusable facts that can later become resume bullets,
  interview stories, or portfolio copy.

If an event has only title/type/time/source, keep it `draft`. Mark it
`needs_review` when ownership, metrics, dates, visibility, or public claims are
unclear. Use `confirmed` only after user confirmation. Do not fabricate missing
context or outcomes to make an event look stronger.

## Event Review Cards

For routine extraction, review in chat instead of generating Markdown files.
Each card should show: title, type, time span, role, organization, location,
status, visibility, evidence/source, uncertain fields, details, claims, and
choices.

```text
Confirm this event / edit fields / mark needs_review / skip this event
```

For 1-5 events, show full cards inline. For 6-12 events, show compact cards,
still one card per event. For 13+ events, show an overview and first 10 cards,
then ask whether to continue or create an external review artifact.

For multi-event extraction, create a JSON draft shaped like
`examples/draft_events.json`. Use `status: draft` unless the user explicitly
confirms the event. After review, import with `import-events`.

## Resume Boundary

When the user asks for a resume, CV, JD match, or job application material:

- Check whether profile basics are present: display name, email, phone, and
  location.
- If basics are missing, ask only for missing fields.
- If relevant events are missing or `needs_review`, continue timeline intake and
  confirmation.
- If timeline facts are ready, provide handoff context for a resume-designer
  workflow.

## Identity Questions

When the user asks what the agent knows about them, asks for professional advice,
or asks about their background, build or read `exports/agent_identity.md` first.
If it is missing or stale, regenerate it with `build-identity`.

## Session Capture

When a session produces career-relevant work, offer to save it as a draft event.
Use `agent_session` as the source type. Summarize the delivered work, not private
chat verbatim, unless the user asks. Include repos, branches, commits, PRs,
files, or published URLs when known. Session events usually start as `draft`.

Suggested prompt:

```text
This session produced career-relevant work. Should I save it to your career
vault as a draft event?
```

## Data Model

- `SourceMaterial`: raw text, file references, URLs, GitHub/project material,
  resume PDFs, job descriptions, notes, and session summaries.
- `CareerEvent`: work, internship, project, education, award, publication,
  certification, scholarship, startup, milestone, or custom timeline unit.
- `Claim`: reusable fact derived from one event; currently stored as strings
  inside each event.
- `Evidence`: source reference supporting a claim; currently represented by
  event `sources`.

Events are flexible. Use relations such as `part_of`, `occurred_during`,
`related_to`, `led_to`, and `resulted_in` when hierarchy or linkage matters.

## Event Extraction Standard

Extract small reusable events, not one generic biography block. One job may
contain several project events; one award, paper, or milestone may be its own
event. Minimum event shape:

```yaml
title: Built Career Timeline Skill
type: project
time:
  start: 2025-05
  end: 2025-08
  precision: month
status: draft
```

Use optional fields when supported: `description`, `role`, `organization`,
`location`, `tags`, `details`, `claims`, `sources`, `relations`, and
`visibility`.

## Scripts

Use `scripts/career_timeline.py` for deterministic file operations:

```bash
python scripts/career_timeline.py --vault ~/.career-vault init
python scripts/career_timeline.py --vault ~/.career-vault add-source --type note --title "Career note" --text "..."
python scripts/career_timeline.py --vault ~/.career-vault add-event --title "Built Career Timeline Skill" --type project --start 2025-05 --description "..."
python scripts/career_timeline.py --vault ~/.career-vault import-events --file examples/draft_events.json
python scripts/career_timeline.py --vault ~/.career-vault list-events
python scripts/career_timeline.py --vault ~/.career-vault profile show --json
python scripts/career_timeline.py --vault ~/.career-vault check-readiness --for resume
python scripts/career_timeline.py --vault ~/.career-vault build-identity
```

## References

- Read `references/vault-format.md` before creating or modifying vault files.
- Read `references/extraction-guide.md` before extracting events from messy
  resumes, notes, links, or project material.

## Output Expectations

When updating the vault, summarize sources added, events or claims changed,
fields marked `needs_review`, and generated export paths. When preparing handoff
context, explain which timeline events/claims were selected and what still needs
user confirmation.
