# Career Vault Resume

Career Vault Resume is a local-first skill and file format for building a
portable career memory from resumes, notes, links, project material, and job
descriptions.

The goal is not to make users fill out another resume form. The goal is to let
an agent carefully extract detailed career events from messy material, save them
in a local vault, and reuse the verified facts for resumes, job applications,
interviews, portfolios, and agent identity.

## What It Does

- Stores raw sources such as resumes, notes, PDFs, links, GitHub summaries, and
  job descriptions.
- Guides an agent to extract small, reusable career events from those sources.
- Stores event-level resume-safe claims and source references.
- Exports an agent-readable identity summary.
- Builds target-job resume context from the local vault.
- Captures career-relevant agent sessions as draft events with user approval.
- Keeps data in portable files that can be committed to Git or moved across
  machines.

The current CLI does not automatically parse resumes, maintain standalone claim
or evidence records, or render final resume PDFs. Those steps require agent
judgment or future commands. Today, the CLI provides deterministic local storage
and basic Markdown exports.

## Repository Layout

```text
career-vault-resume/
  SKILL.md
  README.md
  scripts/
    career_vault.py
  references/
    vault-format.md
    extraction-guide.md
    resume-context.md
  schemas/
    career-event.schema.json
    source-material.schema.json
    claim.schema.json
    vault-profile.schema.json
  assets/
    templates/
      markdown/
        resume_context.md
  examples/
    sample_vault/
```

## Quick Start

Initialize a vault:

```bash
python scripts/career_vault.py --vault ~/.career-vault init
```

Update resume header information:

```bash
python scripts/career_vault.py --vault ~/.career-vault profile update \
  --display-name "Pat Example" \
  --email "pat@example.com" \
  --phone "+1 555 0100" \
  --location "San Francisco, CA"
```

Add a source note:

```bash
python scripts/career_vault.py --vault ~/.career-vault add-source \
  --type note \
  --title "Initial career note" \
  --text "I built a LaTeX resume generator and explored AI rewriting for job-specific resumes."
```

Save a career-relevant agent session summary:

```bash
python scripts/career_vault.py --vault ~/.career-vault add-source \
  --type agent_session \
  --title "Built Career Vault Resume skill" \
  --text "Designed and implemented a local-first career memory skill with schemas, CLI, examples, and tests."
```

Add an event:

```bash
python scripts/career_vault.py --vault ~/.career-vault add-event \
  --title "Built AI Resume Generator" \
  --type project \
  --start 2025-05 \
  --description "Built a template-driven resume generation workflow with AI-assisted rewriting."
```

Import multiple agent-extracted draft events:

```bash
python scripts/career_vault.py --vault ~/.career-vault import-events --file examples/draft_events.json
```

Check whether required resume header fields are present:

```bash
python scripts/career_vault.py --vault ~/.career-vault check-readiness --for resume
```

Build an agent identity summary:

```bash
python scripts/career_vault.py --vault ~/.career-vault build-identity
```

Build resume context for a job description:

```bash
python scripts/career_vault.py --vault ~/.career-vault build-resume-context --jd jd.md
```

## Data Storage

The default vault is a directory:

```text
.career-vault/
  profile.yaml
  events/
  claims/
  sources/
  resumes/
  exports/
```

MVP storage uses human-readable files so users can inspect, migrate, and version
their career memory. A future app can index the same files into SQLite or a
vector store without changing the source of truth.

## Status

This is an early skill-first MVP. It provides the shared data structure and
deterministic file operations. AI extraction should be performed by the host
agent using the instructions in `SKILL.md` and `references/`. The next major
development steps are schema-backed validation, standalone claim storage,
stronger source ingestion, resume drafting, and PDF rendering.
