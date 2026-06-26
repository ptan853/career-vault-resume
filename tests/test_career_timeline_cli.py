import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "career_timeline.py"


def run_cli(vault: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--vault", str(vault), *args],
        check=True,
        text=True,
        capture_output=True,
    )


def test_init_add_event_and_export(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    run_cli(vault, "init")
    run_cli(
        vault,
        "add-event",
        "--title",
        "Career Timeline Skill",
        "--type",
        "project",
        "--start",
        "2025-05",
        "--end",
        "2025-08",
        "--precision",
        "month",
        "--status",
        "confirmed",
        "--description",
        "Built a local-first career timeline workflow.",
        "--claim",
        "Designed a local-first career timeline workflow.",
    )

    listed = run_cli(vault, "list-events", "--json")
    events = json.loads(listed.stdout)
    assert len(events) == 1
    assert events[0]["title"] == "Career Timeline Skill"
    assert events[0]["status"] == "confirmed"

    run_cli(vault, "build-identity")
    identity = vault / "exports" / "agent_identity.md"
    assert identity.exists()
    assert "Career Timeline Skill" in identity.read_text()


def test_agent_session_source_type(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    run_cli(vault, "init")
    result = run_cli(
        vault,
        "add-source",
        "--type",
        "agent_session",
        "--title",
        "Built Career Timeline skill",
        "--text",
        "Implemented a local-first career memory skill.",
    )

    source_path = Path(result.stdout.strip())
    assert source_path.exists()
    assert "Source type: agent_session" in source_path.read_text()


def test_profile_update_show_and_resume_readiness(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    run_cli(vault, "init")

    missing = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--vault",
            str(vault),
            "check-readiness",
            "--for",
            "resume",
        ],
        text=True,
        capture_output=True,
    )
    assert missing.returncode == 1
    assert "display_name" in missing.stdout
    assert "email" in missing.stdout
    assert "phone" in missing.stdout
    assert "location" in missing.stdout

    run_cli(
        vault,
        "profile",
        "update",
        "--display-name",
        "Pat Example",
        "--email",
        "pat@example.com",
        "--phone",
        "+1 555 0100",
        "--location",
        "San Francisco, CA",
        "--include-age",
        "false",
    )

    shown = run_cli(vault, "profile", "show", "--json")
    profile = json.loads(shown.stdout)
    assert profile["user"]["display_name"] == "Pat Example"
    assert profile["user"]["email"] == "pat@example.com"
    assert profile["user"]["phone"] == "+1 555 0100"
    assert profile["user"]["location"] == "San Francisco, CA"
    assert profile["user"]["target_roles"] == []
    assert profile["resume_defaults"]["include_age"] is False

    ready = run_cli(vault, "check-readiness", "--for", "resume")
    assert "Ready for downstream resume handoff" in ready.stdout


def test_init_profile_contains_resume_header_fields(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    run_cli(vault, "init")

    profile_yaml = (vault / "profile.yaml").read_text()
    assert "display_name:" in profile_yaml
    assert "email:" in profile_yaml
    assert "phone:" in profile_yaml
    assert "location:" in profile_yaml
    assert "resume_defaults:" in profile_yaml


def test_import_events_from_agent_draft_file(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    draft = tmp_path / "draft_events.json"
    draft.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "title": "Built Resume Parser",
                        "type": "project",
                        "time": {"start": "2026-01", "precision": "month"},
                        "description": "Built a parser for resume source material.",
                        "claims": ["Built a parser for resume source material."],
                        "sources": ["sources/src_resume.md"],
                    },
                    {
                        "id": "evt_custom_reviewed_project",
                        "title": "Reviewed Career Vault Events",
                        "type": "milestone",
                        "status": "needs_review",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    run_cli(vault, "init")
    result = run_cli(vault, "import-events", "--file", str(draft))
    assert "Imported 2 events" in result.stdout

    listed = run_cli(vault, "list-events", "--json")
    events = json.loads(listed.stdout)
    assert [event["title"] for event in events] == [
        "Built Resume Parser",
        "Reviewed Career Vault Events",
    ]
    assert events[0]["status"] == "draft"
    assert events[0]["time"]["end"] is None
    assert events[0]["visibility"] == "private"
    assert events[1]["id"] == "evt_custom_reviewed_project"
    assert (vault / "events" / "evt_custom_reviewed_project.yaml").exists()


def test_build_identity_includes_profile_background(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    run_cli(vault, "init")
    run_cli(
        vault,
        "profile",
        "update",
        "--display-name",
        "Pat Example",
        "--headline",
        "AI engineer building local-first career tools",
        "--location",
        "San Francisco, CA",
        "--target-role",
        "AI Engineer",
        "--target-role",
        "Developer Tools Engineer",
    )
    run_cli(
        vault,
        "add-event",
        "--title",
        "Built Career Vault",
        "--type",
        "project",
        "--status",
        "confirmed",
        "--description",
        "Built a local career memory vault.",
    )

    run_cli(vault, "build-identity")
    identity = (vault / "exports" / "agent_identity.md").read_text()
    assert "## Professional Profile" in identity
    assert "Pat Example" in identity
    assert "AI engineer building local-first career tools" in identity
    assert "AI Engineer" in identity
    assert "Developer Tools Engineer" in identity
    assert "Built Career Vault" in identity


def test_profile_can_store_optional_photo_path(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    photo = tmp_path / "headshot.jpg"
    photo.write_bytes(b"fake image bytes")

    run_cli(vault, "init")
    run_cli(
        vault,
        "profile",
        "update",
        "--display-name",
        "Pat Example",
        "--email",
        "pat@example.com",
        "--phone",
        "+1 555 0100",
        "--location",
        "San Francisco, CA",
        "--photo-path",
        str(photo),
    )

    shown = run_cli(vault, "profile", "show", "--json")
    profile = json.loads(shown.stdout)
    assert profile["user"]["photo_path"] == str(photo)

    ready = run_cli(vault, "check-readiness", "--for", "resume")
    assert "Ready for downstream resume handoff" in ready.stdout

    run_cli(vault, "build-identity")
    identity = (vault / "exports" / "agent_identity.md").read_text()
    assert "Photo available" in identity


def test_build_basic_resume_outputs_dynamic_editable_files(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    photo = tmp_path / "headshot.jpg"
    photo.write_bytes(b"fake image bytes")

    run_cli(vault, "init")
    run_cli(
        vault,
        "profile",
        "update",
        "--display-name",
        "谭沛烽",
        "--email",
        "peifeng@example.com",
        "--phone",
        "+86 178 0000 0000",
        "--location",
        "长沙",
        "--photo-path",
        str(photo),
        "--target-role",
        "AI算法工程师",
    )
    run_cli(
        vault,
        "add-event",
        "--title",
        "帝国理工大学 - 应用计算科学与工程 - 硕士",
        "--type",
        "education",
        "--start",
        "2023-09",
        "--end",
        "2025-01",
        "--status",
        "confirmed",
        "--description",
        "核心课程：机器学习、应用计算科学、数值方法。",
    )
    run_cli(
        vault,
        "add-event",
        "--title",
        "PM Agent智能项目管理助手",
        "--type",
        "work",
        "--start",
        "2026-03",
        "--status",
        "confirmed",
        "--role",
        "Agent算法工程师",
        "--organization",
        "武汉光庭信息科技",
        "--description",
        "设计并开发基于 LLM Agent 的项目管理助手。",
        "--claim",
        "设计并开发基于 LLM Agent 的项目管理助手。",
    )
    run_cli(
        vault,
        "add-event",
        "--title",
        "通过深度学习预测热带气旋行为",
        "--type",
        "project",
        "--start",
        "2024-03",
        "--status",
        "confirmed",
        "--description",
        "使用 PyTorch 搭建 CNN-ConvLSTM 模型融合图像与数值气象数据。",
    )

    result = run_cli(
        vault,
        "build-basic-resume",
        "--language",
        "zh",
        "--pages",
        "1",
        "--include-photo",
    )
    assert "basic_resume.md" in result.stdout
    assert "basic_resume.html" in result.stdout
    assert "basic_resume.json" in result.stdout

    draft = json.loads((vault / "exports" / "basic_resume.json").read_text())
    assert draft["language"] == "zh"
    assert draft["page_count"] == 1
    assert draft["include_photo"] is True
    assert [section["title"] for section in draft["sections"]] == ["教育背景", "工作经历", "项目经历"]

    markdown = (vault / "exports" / "basic_resume.md").read_text()
    assert "# 谭沛烽" in markdown
    assert "## 工作经历" in markdown
    assert "PM Agent智能项目管理助手" in markdown

    html = (vault / "exports" / "basic_resume.html").read_text()
    assert 'lang="zh"' in html
    assert 'contenteditable="true"' in html
    assert "headshot.jpg" in html
    assert "目标页数：1" in html


def test_add_event_keeps_multiple_non_latin_titles_in_same_second(tmp_path: Path) -> None:
    vault = tmp_path / ".career-vault"
    run_cli(vault, "init")
    run_cli(vault, "add-event", "--title", "中文项目一", "--type", "project")
    run_cli(vault, "add-event", "--title", "中文项目二", "--type", "project")

    listed = run_cli(vault, "list-events", "--json")
    events = json.loads(listed.stdout)
    assert len(events) == 2
    assert {event["title"] for event in events} == {"中文项目一", "中文项目二"}
