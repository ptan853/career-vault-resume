# Vault Format

## Directory Structure

```text
.career-vault/
  profile.yaml
  events/
    evt_*.yaml
  claims/
    claims.jsonl
  sources/
    src_*.md
  resumes/
  exports/
    agent_identity.md
    resume_context.md
```

## Profile

`profile.yaml` stores high-level user preferences and public identity defaults.

```yaml
schema_version: 1
user:
  display_name: ""
  legal_name: ""
  preferred_name: ""
  headline: ""
  email: ""
  phone: ""
  location: ""
  date_of_birth: null
  age: null
  default_locale: en
  target_roles: []
privacy:
  default_visibility: private
  public_summary_allowed: false
resume_defaults:
  include_phone: true
  include_email: true
  include_location: true
  include_age: false
```

Name, email, phone, and current location are resume header fields. Store them in
`profile.yaml`, not as career events. Age is optional and should not be shown by
default; prefer `date_of_birth` only when the user explicitly wants age-related
resume output.

## Career Event

Career events are timeline units. They can represent work, internships,
projects, education, awards, scholarships, publications, courses,
certifications, competitions, open source contributions, startups, milestones,
or custom event types.

Required fields:

- `id`
- `title`
- `type`
- `time`
- `status`

Recommended fields:

- `description`
- `role`
- `organization`
- `location`
- `tags`
- `details`
- `claims`
- `sources`
- `relations`
- `visibility`

Use `details` for flexible fields that should not become first-class schema
fields yet.

## Time

Use the most precise known date:

```yaml
time:
  start: 2025-05
  end: 2025-08
  precision: month
```

Allowed precision values:

- `day`
- `month`
- `year`
- `range`
- `unknown`

If the source does not contain time, keep `start: null`, `end: null`, and
`precision: unknown`.

## Status

Use:

- `draft`: agent extracted but user has not confirmed
- `confirmed`: user confirmed
- `needs_review`: important fields are uncertain
- `archived`: hidden from normal generation but preserved

## Visibility

Use:

- `private`
- `resume`
- `public`

Default to `private` unless the user explicitly says the information is safe to
use publicly.

## Claims

Claims are resume-safe facts. Prefer short, factual, reusable statements.

Good:

```text
Designed a template-driven resume generation workflow.
```

Avoid:

```text
Revolutionized the hiring industry with a world-class AI platform.
```

Claim statuses:

- `draft`
- `confirmed`
- `needs_review`
- `rejected`

## Evidence

Evidence should point back to sources, excerpts, links, or file paths. Do not
discard raw source material after extraction.

## Source Types

Use:

- `note`: user-provided free text
- `resume`: old resume or CV
- `file`: uploaded or local file
- `url`: web link
- `github`: repository or GitHub artifact
- `jd`: job description
- `agent_session`: summary of career-relevant work completed with an agent
