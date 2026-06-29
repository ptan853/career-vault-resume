#!/usr/bin/env python3
"""Small file-based CLI for Career Timeline.

The script intentionally uses only the Python standard library so it can run in
most agent environments without installing dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVENT_TYPES = {
    "work",
    "internship",
    "project",
    "education",
    "research",
    "publication",
    "award",
    "scholarship",
    "certification",
    "course",
    "competition",
    "open_source",
    "volunteer",
    "startup",
    "milestone",
    "custom",
}

EVENT_STATUSES = {"draft", "confirmed", "needs_review", "archived"}
VISIBILITIES = {"private", "resume", "public"}
SOURCE_TYPES = {"note", "resume", "file", "url", "github", "jd", "agent_session"}
RESUME_REQUIRED_PROFILE_FIELDS = ("display_name", "email", "phone", "location")
def default_profile() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "user": {
            "display_name": "",
            "legal_name": "",
            "preferred_name": "",
            "headline": "",
            "email": "",
            "phone": "",
            "location": "",
            "photo_path": None,
            "date_of_birth": None,
            "age": None,
            "default_locale": "en",
            "target_roles": [],
        },
        "privacy": {
            "default_visibility": "private",
            "public_summary_allowed": False,
        },
        "resume_defaults": {
            "include_phone": True,
            "include_email": True,
            "include_location": True,
            "include_age": False,
        },
    }


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:48] or fallback


def compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def vault_path(args: argparse.Namespace) -> Path:
    if args.vault:
        return Path(args.vault).expanduser().resolve()
    return Path.home() / ".career-vault"


def merge_missing(base: dict[str, Any], existing: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in existing.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged[key] = merge_missing(base[key], value)
        else:
            merged[key] = value
    return merged


def parse_yaml_scalar(value: str) -> Any:
    raw = value.strip()
    if raw == "[]":
        return []
    if raw == "null":
        return None
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw.startswith('"') and raw.endswith('"'):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw.strip('"')
    if raw.isdigit():
        return int(raw)
    return raw


def read_profile(vault: Path) -> dict[str, Any]:
    profile = default_profile()
    path = vault / "profile.yaml"
    if not path.exists():
        return profile

    parsed: dict[str, Any] = {}
    section: str | None = None
    list_target: tuple[str, str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if list_target and line.startswith("    - "):
            target_section, target_key = list_target
            parsed.setdefault(target_section, {}).setdefault(target_key, []).append(
                parse_yaml_scalar(line.strip()[2:])
            )
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section = line[:-1]
            list_target = None
            parsed.setdefault(section, {})
            continue
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        value = [] if key == "target_roles" and not raw.strip() else parse_yaml_scalar(raw)
        if key == "target_roles" and not isinstance(value, list):
            value = []
        list_target = (section, key) if section and key == "target_roles" and isinstance(value, list) else None
        if line.startswith("  ") and section:
            parsed.setdefault(section, {})[key] = value
        else:
            parsed[key] = value
            section = None
            list_target = None
    return merge_missing(profile, parsed)


def write_profile(vault: Path, profile: dict[str, Any]) -> None:
    write_yaml(vault / "profile.yaml", profile)


def ensure_vault(vault: Path) -> None:
    for dirname in ("events", "claims", "sources", "resumes", "exports"):
        (vault / dirname).mkdir(parents=True, exist_ok=True)
    profile = vault / "profile.yaml"
    if not profile.exists():
        write_profile(vault, default_profile())
    else:
        current = read_profile(vault)
        for section, defaults in default_profile().items():
            if isinstance(defaults, dict):
                for key in defaults:
                    if key not in current.get(section, {}):
                        write_profile(vault, current)
                        return


def parse_kv(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Expected KEY=VALUE, got: {value}")
        key, raw = value.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Empty key in detail: {value}")
        parsed[key] = raw.strip()
    return parsed


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if not text:
        return '""'
    if re.fullmatch(r"[A-Za-z0-9_./:@+-]+", text) and text not in {"null", "true", "false"}:
        return text
    return json.dumps(text, ensure_ascii=False)


def yaml_block(data: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, list) and not value:
                lines.append(f"{prefix}{key}: []")
                continue
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(yaml_block(value, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {yaml_scalar(value)}")
        return lines
    if isinstance(data, list):
        lines = []
        if not data:
            return [f"{prefix}[]"]
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(yaml_block(item, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_scalar(item)}")
        return lines
    return [f"{prefix}{yaml_scalar(data)}"]


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text("\n".join(yaml_block(data)) + "\n", encoding="utf-8")


def read_event(path: Path) -> dict[str, Any]:
    # Event files are written as YAML-like JSON-compatible scalars. For robust
    # export without a YAML dependency, keep a hidden JSON copy next to each file.
    json_path = path.with_suffix(".json")
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))
    return {"id": path.stem, "title": path.stem, "status": "needs_review"}


def write_event(vault: Path, event: dict[str, Any]) -> Path:
    event_id = event["id"]
    yaml_path = vault / "events" / f"{event_id}.yaml"
    json_path = vault / "events" / f"{event_id}.json"
    write_yaml(yaml_path, event)
    json_path.write_text(json.dumps(event, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return yaml_path


def unique_event_id(vault: Path, title: str, provided_id: str | None = None) -> str:
    if provided_id:
        return provided_id
    base = f"evt_{compact_timestamp()}_{slugify(title, 'event')}"
    event_id = base
    counter = 2
    while (vault / "events" / f"{event_id}.yaml").exists():
        event_id = f"{base}_{counter}"
        counter += 1
    return event_id


def normalize_draft_event(vault: Path, raw: dict[str, Any]) -> dict[str, Any]:
    title = str(raw.get("title") or "").strip()
    if not title:
        raise SystemExit("Imported event is missing title")
    event_type = raw.get("type")
    if event_type not in EVENT_TYPES:
        raise SystemExit(f"Unsupported event type: {event_type}")
    status = raw.get("status", "draft")
    if status not in EVENT_STATUSES:
        raise SystemExit(f"Unsupported status: {status}")
    visibility = raw.get("visibility", "private")
    if visibility not in VISIBILITIES:
        raise SystemExit(f"Unsupported visibility: {visibility}")
    raw_time = raw.get("time") or {}
    if not isinstance(raw_time, dict):
        raise SystemExit(f"Expected time object for imported event: {title}")
    precision = raw_time.get("precision", "unknown")
    if precision not in {"day", "month", "year", "range", "unknown"}:
        raise SystemExit(f"Unsupported time precision: {precision}")
    timestamp = now_iso()
    return {
        "schema_version": 1,
        "id": unique_event_id(vault, title, raw.get("id")),
        "title": title,
        "type": event_type,
        "custom_type": raw.get("custom_type"),
        "time": {
            "start": raw_time.get("start"),
            "end": raw_time.get("end"),
            "precision": precision,
        },
        "status": status,
        "description": raw.get("description", ""),
        "role": raw.get("role"),
        "organization": raw.get("organization"),
        "location": raw.get("location"),
        "tags": raw.get("tags", []),
        "details": raw.get("details", {}),
        "claims": raw.get("claims", []),
        "sources": raw.get("sources", []),
        "relations": raw.get("relations", []),
        "visibility": visibility,
        "created_at": raw.get("created_at", timestamp),
        "updated_at": timestamp,
    }


def load_draft_events(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    events = data.get("events") if isinstance(data, dict) else data
    if not isinstance(events, list):
        raise SystemExit("Import file must be a JSON list or an object with an events list")
    for event in events:
        if not isinstance(event, dict):
            raise SystemExit("Each imported event must be a JSON object")
    return events


def command_init(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    print(f"Initialized career vault: {vault}")


def command_add_source(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    source_id = f"src_{compact_timestamp()}_{slugify(args.title, 'source')}"
    source_path = vault / "sources" / f"{source_id}.md"
    if args.file:
        original = Path(args.file).expanduser().resolve()
        if not original.exists():
            raise SystemExit(f"Source file does not exist: {original}")
        stored = vault / "sources" / f"{source_id}{original.suffix}"
        shutil.copy2(original, stored)
        body = f"# {args.title}\n\nSource type: {args.type}\nOriginal file: {original}\nStored file: {stored.name}\n"
    elif args.url:
        body = f"# {args.title}\n\nSource type: {args.type}\nURL: {args.url}\n\n"
    else:
        body = f"# {args.title}\n\nSource type: {args.type}\n\n{args.text or ''}\n"
    source_path.write_text(body, encoding="utf-8")
    print(source_path)


def command_add_event(args: argparse.Namespace) -> None:
    if args.type not in EVENT_TYPES:
        raise SystemExit(f"Unsupported event type: {args.type}")
    if args.status not in EVENT_STATUSES:
        raise SystemExit(f"Unsupported status: {args.status}")
    if args.visibility not in VISIBILITIES:
        raise SystemExit(f"Unsupported visibility: {args.visibility}")
    vault = vault_path(args)
    ensure_vault(vault)
    event_id = unique_event_id(vault, args.title, args.id)
    event = {
        "schema_version": 1,
        "id": event_id,
        "title": args.title,
        "type": args.type,
        "custom_type": args.custom_type,
        "time": {
            "start": args.start,
            "end": args.end,
            "precision": args.precision,
        },
        "status": args.status,
        "description": args.description or "",
        "role": args.role,
        "organization": args.organization,
        "location": args.location,
        "tags": args.tag,
        "details": parse_kv(args.detail),
        "claims": args.claim,
        "sources": args.source,
        "relations": [],
        "visibility": args.visibility,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    path = write_event(vault, event)
    print(path)


def command_import_events(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    import_path = Path(args.file).expanduser().resolve()
    if not import_path.exists():
        raise SystemExit(f"Import file does not exist: {import_path}")
    raw_events = load_draft_events(import_path)
    paths = [write_event(vault, normalize_draft_event(vault, raw)) for raw in raw_events]
    print(f"Imported {len(paths)} events")
    for path in paths:
        print(path)


def command_list_events(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    events = [read_event(path) for path in sorted((vault / "events").glob("evt_*.yaml"))]
    if args.json:
        print(json.dumps(events, indent=2, ensure_ascii=False))
        return
    for event in events:
        time = event.get("time", {})
        start = time.get("start") or "unknown"
        end = time.get("end") or ""
        span = f"{start}..{end}" if end else start
        print(f"{event.get('id')} | {span} | {event.get('type')} | {event.get('status')} | {event.get('title')}")


def load_events(vault: Path) -> list[dict[str, Any]]:
    return [read_event(path) for path in sorted((vault / "events").glob("evt_*.yaml"))]


def command_build_identity(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    profile = read_profile(vault)
    user = profile.get("user", {})
    events = load_events(vault)
    confirmed = [event for event in events if event.get("status") == "confirmed"]
    draft = [event for event in events if event.get("status") != "confirmed"]
    lines = [
        "# Agent Identity",
        "",
        "This file is generated from the local career vault. Treat it as context, not as permission to invent facts.",
        "",
        "## Professional Profile",
        "",
    ]
    profile_lines = []
    if user.get("display_name"):
        profile_lines.append(f"- Name: {user['display_name']}")
    if user.get("preferred_name"):
        profile_lines.append(f"- Preferred name: {user['preferred_name']}")
    if user.get("headline"):
        profile_lines.append(f"- Headline: {user['headline']}")
    if user.get("location"):
        profile_lines.append(f"- Location: {user['location']}")
    if user.get("photo_path"):
        profile_lines.append("- Photo available: yes")
    target_roles = user.get("target_roles") or []
    if target_roles:
        profile_lines.append(f"- Target roles: {', '.join(target_roles)}")
    lines.extend(profile_lines or ["No profile summary has been confirmed yet."])
    lines.extend([
        "",
        "## Confirmed Career Events",
        "",
    ])
    for event in confirmed:
        lines.extend(format_event_markdown(event))
    if not confirmed:
        lines.append("No confirmed events yet.")
    lines.extend(["", "## Draft Or Review-Needed Events", ""])
    for event in draft:
        lines.extend(format_event_markdown(event))
    if not draft:
        lines.append("No draft events.")
    output = vault / "exports" / "agent_identity.md"
    output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(output)


def format_event_markdown(event: dict[str, Any]) -> list[str]:
    time = event.get("time", {})
    span = time.get("start") or "unknown"
    if time.get("end"):
        span = f"{span} to {time['end']}"
    lines = [
        f"### {event.get('title', event.get('id'))}",
        "",
        f"- Type: {event.get('type')}",
        f"- Time: {span}",
        f"- Status: {event.get('status')}",
    ]
    if event.get("role"):
        lines.append(f"- Role: {event['role']}")
    if event.get("organization"):
        lines.append(f"- Organization: {event['organization']}")
    if event.get("description"):
        lines.extend(["", event["description"]])
    claims = event.get("claims") or []
    if claims:
        lines.extend(["", "Claims:"])
        lines.extend([f"- {claim}" for claim in claims])
    lines.append("")
    return lines



def command_profile_show(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    profile = read_profile(vault)
    if args.json:
        print(json.dumps(profile, indent=2, ensure_ascii=False))
        return
    user = profile["user"]
    print(f"Name: {user.get('display_name') or '(missing)'}")
    print(f"Email: {user.get('email') or '(missing)'}")
    print(f"Phone: {user.get('phone') or '(missing)'}")
    print(f"Location: {user.get('location') or '(missing)'}")


def parse_bool_arg(value: str) -> bool:
    lowered = value.lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError("Expected true or false")


def command_profile_update(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    profile = read_profile(vault)
    user_updates = {
        "display_name": args.display_name,
        "legal_name": args.legal_name,
        "preferred_name": args.preferred_name,
        "headline": args.headline,
        "email": args.email,
        "phone": args.phone,
        "location": args.location,
        "photo_path": args.photo_path,
        "date_of_birth": args.date_of_birth,
        "age": args.age,
        "default_locale": args.default_locale,
    }
    for key, value in user_updates.items():
        if value is not None:
            profile["user"][key] = value
    if args.target_role is not None:
        profile["user"]["target_roles"] = args.target_role
    if args.include_age is not None:
        profile["resume_defaults"]["include_age"] = args.include_age
    write_profile(vault, profile)
    print(vault / "profile.yaml")


def command_check_readiness(args: argparse.Namespace) -> None:
    vault = vault_path(args)
    ensure_vault(vault)
    profile = read_profile(vault)
    if args.readiness_for != "resume":
        raise SystemExit(f"Unsupported readiness target: {args.readiness_for}")
    missing = [
        field
        for field in RESUME_REQUIRED_PROFILE_FIELDS
        if not str(profile["user"].get(field) or "").strip()
    ]
    if missing:
        print("Missing required resume profile fields:")
        for field in missing:
            print(f"- {field}")
        raise SystemExit(1)
    print("Ready for downstream resume handoff")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Career Timeline file CLI")
    parser.add_argument("--vault", help="Path to .career-vault directory")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize a career vault")
    init.set_defaults(func=command_init)

    source = sub.add_parser("add-source", help="Add raw source material")
    source.add_argument("--type", required=True, choices=sorted(SOURCE_TYPES))
    source.add_argument("--title", required=True)
    source.add_argument("--text", default="")
    source.add_argument("--file")
    source.add_argument("--url")
    source.set_defaults(func=command_add_source)

    event = sub.add_parser("add-event", help="Add a structured career event")
    event.add_argument("--id")
    event.add_argument("--title", required=True)
    event.add_argument("--type", required=True, choices=sorted(EVENT_TYPES))
    event.add_argument("--custom-type")
    event.add_argument("--start")
    event.add_argument("--end")
    event.add_argument("--precision", default="unknown", choices=["day", "month", "year", "range", "unknown"])
    event.add_argument("--status", default="draft", choices=sorted(EVENT_STATUSES))
    event.add_argument("--description")
    event.add_argument("--role")
    event.add_argument("--organization")
    event.add_argument("--location")
    event.add_argument("--tag", action="append", default=[])
    event.add_argument("--detail", action="append", default=[], help="Custom detail as KEY=VALUE")
    event.add_argument("--claim", action="append", default=[])
    event.add_argument("--source", action="append", default=[])
    event.add_argument("--visibility", default="private", choices=sorted(VISIBILITIES))
    event.set_defaults(func=command_add_event)

    import_events = sub.add_parser("import-events", help="Import agent-extracted draft events from JSON")
    import_events.add_argument("--file", required=True, help="Path to a JSON list or object with an events list")
    import_events.set_defaults(func=command_import_events)

    list_events = sub.add_parser("list-events", help="List career events")
    list_events.add_argument("--json", action="store_true")
    list_events.set_defaults(func=command_list_events)

    identity = sub.add_parser("build-identity", help="Export agent identity summary")
    identity.set_defaults(func=command_build_identity)


    profile = sub.add_parser("profile", help="Show or update vault profile")
    profile_sub = profile.add_subparsers(dest="profile_command", required=True)

    profile_show = profile_sub.add_parser("show", help="Show vault profile")
    profile_show.add_argument("--json", action="store_true")
    profile_show.set_defaults(func=command_profile_show)

    profile_update = profile_sub.add_parser("update", help="Update vault profile")
    profile_update.add_argument("--display-name")
    profile_update.add_argument("--legal-name")
    profile_update.add_argument("--preferred-name")
    profile_update.add_argument("--headline")
    profile_update.add_argument("--email")
    profile_update.add_argument("--phone")
    profile_update.add_argument("--location")
    profile_update.add_argument("--photo-path")
    profile_update.add_argument("--date-of-birth")
    profile_update.add_argument("--age", type=int)
    profile_update.add_argument("--default-locale")
    profile_update.add_argument("--target-role", action="append")
    profile_update.add_argument("--include-age", type=parse_bool_arg)
    profile_update.set_defaults(func=command_profile_update)

    readiness = sub.add_parser("check-readiness", help="Check vault readiness for an output")
    readiness.add_argument("--for", dest="readiness_for", required=True, choices=["resume"])
    readiness.set_defaults(func=command_check_readiness)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
