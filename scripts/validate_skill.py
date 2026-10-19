#!/usr/bin/env python3
"""Validate the repository skill without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}"),
    re.compile(r"gho_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
ABS_HOME_PATTERN = re.compile(r"/Users/[A-Za-z0-9._-]+/")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".txt", ".py", ".json", ".sh"}


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name == ".gitignore"):
            yield path


def validate_frontmatter(skill: Path, errors: list[str]) -> None:
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
        return

    end = text.find("\n---\n", 4)
    if end == -1:
        errors.append("SKILL.md frontmatter is not closed")
        return

    frontmatter = text[4:end]
    body = text[end + 5 :].strip()
    name_match = re.search(r"^name:\s*(\S+)\s*$", frontmatter, re.MULTILINE)
    if not name_match:
        errors.append("SKILL.md is missing a scalar name field")
    elif name_match.group(1) != skill.parent.name:
        errors.append(
            f"skill name {name_match.group(1)!r} does not match folder "
            f"{skill.parent.name!r}"
        )
    if not re.search(r"^description:\s*", frontmatter, re.MULTILINE):
        errors.append("SKILL.md is missing a description field")
    if not body:
        errors.append("SKILL.md body is empty")


def validate_links(root: Path, errors: list[str]) -> None:
    for path in iter_text_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for target in LINK_PATTERN.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target:
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(root)}: broken link {target!r}")


def validate_hygiene(root: Path, errors: list[str]) -> None:
    todo_marker = "TO" + "DO"
    for path in iter_text_files(root):
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8", errors="replace")
        if f"[{todo_marker}" in text or f"{todo_marker}:" in text:
            errors.append(f"{rel}: unfinished TODO marker")
        if ABS_HOME_PATTERN.search(text):
            errors.append(f"{rel}: contains an absolute /Users/... path")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel}: possible credential pattern")
                break


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    skill = root / "SKILL.md"
    errors: list[str] = []

    if not skill.exists():
        print(f"ERROR: missing {skill}")
        return 2

    validate_frontmatter(skill, errors)
    validate_links(root, errors)
    validate_hygiene(root, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    text_files = list(iter_text_files(root))
    total_bytes = sum(path.stat().st_size for path in text_files)
    print("Skill is valid.")
    print(f"text_files={len(text_files)} bytes={total_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
