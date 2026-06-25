# Extraction Guide

Use this guide when converting resumes, notes, links, or project material into
career events.

## Extraction Principles

- Extract detailed events, not one generic resume block.
- Preserve the source before summarizing it.
- Split separate projects, awards, publications, roles, and milestones when they
  may be useful independently.
- Keep overlapping dates if the source supports them.
- Use relations instead of forcing one hierarchy.
- Mark uncertainty explicitly.
- For agent sessions, summarize the delivered work and ask before storing it.

## What Counts as an Event

Create events for:

- jobs and internships
- projects inside jobs or outside jobs
- education entries
- awards and scholarships
- publications and research
- certifications and courses
- competitions
- open source contributions
- startups and products
- meaningful milestones
- career-relevant agent sessions that produced a project, release, document,
  public artifact, interview preparation, or job application material

Do not create events for vague claims without evidence unless they are marked
`needs_review`.

## Suggested Extraction Passes

1. Read the whole source once and identify time spans.
2. Extract role-level events such as jobs, internships, and education.
3. Extract project-level events inside those roles.
4. Extract awards, publications, certifications, and milestones.
5. Generate draft claims for each event.
6. Add `needs_review` to missing dates, vague metrics, unclear ownership, or
   unsupported impact.
7. Present the draft event list to the user for review.
8. Save reviewed events as JSON and import them with `import-events`.

## Draft Import Format

For multi-event extraction, write a JSON file with an `events` array. See
`examples/draft_events.json`.

Minimum event object:

```json
{
  "title": "Built AI Resume Generator",
  "type": "project",
  "time": {
    "start": "2025-05",
    "precision": "month"
  },
  "description": "Built a template-driven resume generation workflow.",
  "claims": ["Designed a template-driven resume generation workflow."],
  "sources": ["sources/src_sample_resume.md"]
}
```

The CLI fills missing `id`, `schema_version`, `status`, `visibility`, `end`,
timestamps, and optional fields. Use explicit `status: confirmed` only when the
user has confirmed the event.

## Agent Session Extraction

When extracting from the current agent session:

1. Identify the artifact or outcome that was actually produced.
2. Record the repo, files, commit, branch, PR, URL, or generated artifact when
   available.
3. Write the event as a project, milestone, open source contribution, resume
   preparation event, or custom event.
4. Keep status as `draft` unless the user explicitly confirms it.
5. Avoid storing private raw chat unless the user asks.
6. Mark unclear ownership, dates, and public visibility as `needs_review`.

Useful claims from a session should be concrete:

- Implemented a file-based CLI for maintaining a local career vault.
- Defined JSON Schemas for career events, sources, claims, and profile metadata.
- Published an initial open-source skill repository on GitHub.

## Event Type Guidance

Use `work` for full-time roles and `internship` for internships. Use `project`
for concrete things built or delivered. Use `research` for research activity and
`publication` for accepted or published artifacts. Use `award` or `scholarship`
when the source describes recognition.

Use `custom` only when the event does not fit the recommended type list.

## Relation Guidance

Use:

- `part_of` when one event belongs under another
- `occurred_during` when the timing overlaps but ownership is not hierarchical
- `related_to` when two events share context
- `led_to` when one event caused another
- `resulted_in` when an event produced an award, publication, or outcome

## Review Questions

Ask follow-up questions when:

- date is missing
- organization or role is unclear
- metrics are impressive but unsupported
- project ownership is ambiguous
- source language is unclear or translation may change meaning
- the event seems useful for resumes but lacks claims
