#!/usr/bin/env python3
"""Consistency checks for the kit. Run before committing: python3 scripts/check.py

Checks frontmatter, skill references, links, README coverage, version markers, the
always-on word budget, shell script syntax, and (when mmdc is installed) Mermaid rendering.
Exits 1 if any problem is found.
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
KIT = REPO / "kit"
AGENTS_DIR = KIT / ".claude/agents"
SKILLS_DIR = KIT / ".claude/skills"
AGREEMENT_WORD_BUDGET = 700  # kit/AGENTS.md is loaded into every conversation
AGENT_FIELDS = {"name", "description", "model", "skills"}
MODELS = {"haiku", "sonnet", "opus", "inherit"}

problems = []


def rel(path):
    return path.relative_to(REPO).as_posix()


def frontmatter(path):
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        problems.append(f"{rel(path)}: no frontmatter")
        return {}, text
    fields, key = {}, None
    for line in match.group(1).splitlines():
        item = re.match(r"^\s+- (.+)$", line)
        if item:
            fields.setdefault(key, [])
            if isinstance(fields[key], list):
                fields[key].append(item.group(1).strip())
        else:
            key, _, value = line.partition(":")
            key = key.strip()
            fields[key] = value.strip() or []
    return fields, text


def skill_mentions(text):
    return set(re.findall(r"`([a-z0-9-]+)` skill", text))


def without_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


skills = {}
for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
    fields, text = frontmatter(path)
    name, description = fields.get("name"), fields.get("description")
    if name != path.parent.name:
        problems.append(f"{rel(path)}: name '{name}' doesn't match folder '{path.parent.name}'")
    if not name or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append(f"{rel(path)}: name must be lowercase words joined by hyphens, at most 64 characters")
    if not description or len(description) > 1024:
        problems.append(f"{rel(path)}: description missing or longer than 1024 characters")
    skills[path.parent.name] = text

for path in sorted(AGENTS_DIR.glob("*.md")):
    fields, text = frontmatter(path)
    if fields.get("name") != path.stem:
        problems.append(f"{rel(path)}: name '{fields.get('name')}' doesn't match file name")
    if not fields.get("description"):
        problems.append(f"{rel(path)}: no description")
    extra = set(fields) - AGENT_FIELDS
    if extra:
        problems.append(f"{rel(path)}: unsupported fields {sorted(extra)} (allowed: {sorted(AGENT_FIELDS)})")
    if "model" in fields and fields["model"] not in MODELS:
        problems.append(f"{rel(path)}: model '{fields['model']}' is not one of {sorted(MODELS)}")
    preload = fields.get("skills") if isinstance(fields.get("skills"), list) else []
    for skill in set(preload) | skill_mentions(text):
        if skill not in skills:
            problems.append(f"{rel(path)}: refers to missing skill '{skill}'")
    # Framework developers: <name>-developer preloads implementation and its <name> skill.
    if path.stem.endswith("-developer"):
        framework = path.stem[: -len("-developer")]
        for required in ("implementation", framework):
            if required not in preload:
                problems.append(f"{rel(path)}: framework developer must preload the '{required}' skill")
        if framework in skills:
            for heading in (r"^## Tests$", r"^## (Always )?Stop and report before$"):
                if not re.search(heading, skills[framework], re.M | re.I):
                    problems.append(f"kit/.claude/skills/{framework}/SKILL.md: framework skill needs a "
                                    f"'{heading.strip('^$')}' section")

for path in [KIT / "AGENTS.md", *SKILLS_DIR.glob("*/SKILL.md")]:
    for skill in skill_mentions(path.read_text()):
        if skill not in skills:
            problems.append(f"{rel(path)}: refers to missing skill '{skill}'")

for path in [REPO / "README.md", REPO / "CHANGELOG.md", REPO / "AGENTS.md", *KIT.rglob("*.md")]:
    for link in re.findall(r"\]\(([^)#\s]+)", without_code(path.read_text())):
        if not re.match(r"[a-z]+:", link) and not (path.parent / link).exists():
            problems.append(f"{rel(path)}: broken link '{link}'")

readme = (REPO / "README.md").read_text()
for path in [*AGENTS_DIR.glob("*.md"), *SKILLS_DIR.glob("*/SKILL.md")]:
    if rel(path) not in readme:
        problems.append(f"README.md doesn't list {rel(path)}")

if (KIT / "CLAUDE.md").read_text() != "@AGENTS.md\n":
    problems.append("kit/CLAUDE.md must contain only '@AGENTS.md'")

version = (REPO / "VERSION").read_text().strip()
agreement = (KIT / "AGENTS.md").read_text()
if "\n## This project" not in agreement:
    problems.append("kit/AGENTS.md has no '## This project' section (scripts/sync.sh relies on it)")
marker = re.search(r"agentic-defaults (\d+\.\d+\.\d+)", agreement)
if not marker or marker.group(1) != version:
    problems.append(f"kit/AGENTS.md version marker doesn't match VERSION {version}")
changelog = re.search(r"^## (\d+\.\d+\.\d+)", (REPO / "CHANGELOG.md").read_text(), re.M)
if not changelog or changelog.group(1) != version:
    problems.append(f"CHANGELOG.md's newest entry doesn't match VERSION {version}")
words = len(agreement.split())
if words > AGREEMENT_WORD_BUDGET:
    problems.append(f"kit/AGENTS.md has {words} words, over the {AGREEMENT_WORD_BUDGET}-word budget")

for script in [*KIT.rglob("*.sh"), *(REPO / "scripts").glob("*.sh")]:
    result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    if result.returncode != 0:
        problems.append(f"{rel(script)}: syntax error: {result.stderr.strip()}")

mermaid_files = [p for p in [REPO / "README.md", *KIT.rglob("*.md")] if "```mermaid" in p.read_text()]
if shutil.which("mmdc"):
    with tempfile.TemporaryDirectory() as out:
        for path in mermaid_files:
            result = subprocess.run(["mmdc", "-q", "-i", str(path), "-o", f"{out}/{path.name}"],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                problems.append(f"{rel(path)}: Mermaid diagram doesn't render: {result.stderr.strip()[:200]}")
    mermaid_note = f"{len(mermaid_files)} files with diagrams rendered"
else:
    mermaid_note = "Mermaid rendering skipped (mmdc not installed)"

print(f"Checked {len(skills)} skills, {len(list(AGENTS_DIR.glob('*.md')))} agents, "
      f"kit/AGENTS.md at {words}/{AGREEMENT_WORD_BUDGET} words, version {version}. {mermaid_note}.")
if problems:
    print("\nProblems:")
    for problem in problems:
        print(f"- {problem}")
    sys.exit(1)
print("No problems found.")
