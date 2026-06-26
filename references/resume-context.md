# Downstream Handoff Context

Use this guide only when a downstream resume, cover-letter, interview, or
portfolio workflow needs verified facts from the career timeline. This file does
not define the final resume-writing process.

## Inputs

- Target request or job description, when available
- Confirmed or draft career events
- Confirmed or review-needed claims
- User preferences and target locale, when known
- Downstream constraints, when provided by another skill or tool

## Selection Rules

- Prefer confirmed claims and confirmed events.
- Include draft or `needs_review` facts only if clearly marked.
- Select events by relevance to responsibilities, skills, domain, seniority, and
  evidence quality.
- Do not fabricate missing metrics, technologies, employers, dates, or awards.
- Preserve user truth over keyword matching.

## Handoff Output

Produce `exports/resume_context.md` only as a facts handoff with:

- target request summary
- selected events
- selected claims
- missing information questions
- suggested positioning notes
- risk notes for unsupported facts

The CLI also keeps legacy `basic_resume.*` exports for compatibility and quick
manual inspection:

- `exports/basic_resume.json`
- `exports/basic_resume.md`
- `exports/basic_resume.html`

Treat these as diagnostics, not final application resumes. Final section choice,
JD analysis, bullet rewriting, visual design, editable output, and PDF rendering
belong in a separate resume-designer workflow.

## Readiness Checks

Before handoff, verify:

- profile basics: name, email, phone, and current location
- target role or target request, if relevant
- enough confirmed events for the requested artifact
- important draft or `needs_review` facts are clearly labeled
- optional photo/headshot path is present only if the downstream template needs
  one

If essentials are missing, ask only for the missing fields and stay in timeline
intake until the user confirms the facts.

## What Not To Do Here

- Do not decide the final resume section structure.
- Do not rewrite every event into application bullets.
- Do not choose visual templates, page count, or PDF layout.
- Do not move private events into public artifacts without user permission.
- Do not treat `basic_resume.md` or `basic_resume.html` as final output.
