# Manual Skill Evals

Use these evals before merging changes to `SKILL.md`, workflow references, or
agent-facing examples. The goal is to verify agent behavior, not just CLI
syntax.

## Setup

Use a fresh agent session and a disposable vault unless you are intentionally
checking the real user vault.

```bash
export CAREER_TIMELINE_TEST_VAULT=/tmp/career-timeline-eval
rm -rf "$CAREER_TIMELINE_TEST_VAULT"
python scripts/career_timeline.py --vault "$CAREER_TIMELINE_TEST_VAULT" init
```

A passing run means the agent follows the timeline boundary: source -> draft
events -> user review -> confirmed timeline -> identity/handoff. It must not
skip straight to final resume writing.

## Eval 1: Identity Lookup

Prompt:

```text
你知道我是谁吗？
```

Expected behavior:

- The agent uses the career-timeline skill.
- It checks for an existing vault and `exports/agent_identity.md` before making
  user-specific claims.
- If identity data is missing, it says so and asks for only essential profile
  fields: name, email, phone, and location.
- It does not invent identity details from filesystem paths or prior vague
  context.

Fail if:

- The agent confidently claims to know the user without vault evidence.
- The agent ignores the vault entirely.
- The agent asks for a long onboarding form before the basics.

## Eval 2: Profile Initialization

Prompt:

```text
可以，姓名是 Pat Example，邮箱 pat@example.com，电话 +1 555 0100，现居 San Francisco，目前是 AI Engineer。
```

Expected behavior:

- The agent updates `profile.yaml` with stable identity fields.
- Age is not requested or stored by default.
- Photo/headshot is mentioned only as optional downstream profile data.
- The agent builds or offers to build `exports/agent_identity.md`.

CLI spot check:

```bash
python scripts/career_timeline.py --vault "$CAREER_TIMELINE_TEST_VAULT" profile show --json
python scripts/career_timeline.py --vault "$CAREER_TIMELINE_TEST_VAULT" build-identity
```

Fail if:

- The agent stores profile basics as a timeline event.
- The agent treats photo or age as required.

## Eval 3: Source To Event Cards

Prompt:

```text
这是一个项目经历：2025.05 到 2025.08，我做了 Career Timeline Skill，用 Python 实现本地 vault、source 保存、event 导入和 agent_identity.md 导出。
```

Expected behavior:

- The agent saves the raw material as a source first, or clearly states it will
  preserve the source before import.
- It extracts at least one draft `CareerEvent`.
- It shows an event review card in chat with title, type, time, role or unknown,
  organization or none, evidence, details, claims, status, visibility, uncertain
  fields, and choices.
- It waits for user confirmation before importing as confirmed.

Fail if:

- The agent writes directly to confirmed timeline without review.
- The agent creates only a summary paragraph instead of an event card.
- The agent creates a Markdown review file for a routine small batch.

## Eval 4: Multi-Event Batch Discipline

Prompt:

```text
我有 8 个经历：两个学校、两段工作、三个项目、一个奖学金。你帮我整理进 timeline。
```

Expected behavior:

- The agent asks for or uses the supplied source details.
- It presents compact event cards, one card per event.
- It does not collapse all events into one generic resume block.
- It asks whether to confirm, edit, mark `needs_review`, or skip each event or
  the batch.

Fail if:

- The agent says only “我找到了 8 个事件” without showing cards.
- The agent imports all events without review.
- The agent turns the batch into a resume draft.

## Eval 5: Project Material Detail

Prompt:

```text
这个 GitHub 项目是一个 AI 命令行工具，README 说它支持 TUI、LLM tool routing、workspace sandbox、SOP plan 渲染和单元测试。我主要负责 SOP plan 数据模型、风险摘要渲染、step order 处理，以及把几个工具迁移到统一 action discovery。
```

Expected behavior:

- The agent creates a project/open-source draft event, not a final resume bullet.
- The event card includes context, contribution, implementation, outcome or
  artifact, evidence/source, reusable claims, and needs-review items.
- Claims are specific enough to rewrite later, such as structured SOP plan data
  model, risk-summary rendering, step ordering, or action discovery migration.
- The agent marks ownership, metrics, release status, and public visibility as
  `needs_review` if they are not explicitly confirmed.

Fail if:

- The event says only “worked on an AI CLI project.”
- The agent invents metrics, leadership, public release status, or production
  adoption.
- The agent stores the event as confirmed without user confirmation.

## Eval 6: Resume Boundary

Prompt:

```text
帮我根据这个 JD 做一份简历。
```

Expected behavior:

- The agent uses career-timeline only to check profile and event readiness.
- If essentials are missing, it asks only for missing profile fields or missing
  event facts.
- If the timeline is ready, it produces handoff guidance or context for a
  downstream resume-designer workflow.
- It does not generate or present a final application resume.

Fail if:

- The agent directly writes a full final resume inside this skill.
- The agent chooses visual templates, page layout, or PDF export here.
- The agent copies event claims unchanged as polished resume bullets without a
  downstream rewrite step.

## CLI Smoke Checks

Run these after editing CLI-facing text or examples:

```bash
python scripts/career_timeline.py --help
python scripts/career_timeline.py --vault /tmp/career-timeline-eval init
python scripts/career_timeline.py --vault /tmp/career-timeline-eval import-events --file examples/draft_events.json
python scripts/career_timeline.py --vault /tmp/career-timeline-eval build-identity
python scripts/career_timeline.py --vault /tmp/career-timeline-eval check-readiness --for resume
PYTHONPYCACHEPREFIX=/tmp/career-timeline-pycache python3 -m py_compile scripts/career_timeline.py tests/test_career_timeline_cli.py
python3 -c 'import json, pathlib; [json.loads(p.read_text()) for p in pathlib.Path("schemas").glob("*.json")]; json.loads(pathlib.Path("examples/draft_events.json").read_text())'
git diff --check
```

Expected readiness wording:

```text
Ready for downstream resume handoff
```

## Keyword Regression Check

Run:

```bash
rg -n "AI Resume Generator|ai_resume_generator|resume generation|resume-safe|Ready for resume generation|final resume generation|Generate a simple editable resume|photo cropping|career-vault-resume|career_vault" . --glob "!evals/manual-skill-evals.md"
```

Expected result: no matches, except in intentional historical notes if clearly
labeled as such.

## Reporting

For each eval, record:

- prompt used
- pass/fail
- observed agent behavior
- files created or changed
- any loophole the agent used to avoid the intended workflow

If an eval fails, update `SKILL.md` or the relevant reference file with the
smallest rule that closes the loophole, then rerun the failed scenario.
