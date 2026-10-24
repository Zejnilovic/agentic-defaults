#!/usr/bin/env python3
"""Consistency checks for the kit. Run before committing: python3 scripts/check.py

Checks frontmatter, skill references, links, README coverage, version markers, packs, the
always-on word budget, shell script syntax, and (when mmdc is installed) Mermaid rendering.
Exits 1 if any problem is found.
"""

import json
import os
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

preloads = {}
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
    preloads[path.stem] = preload
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

for path in [REPO / "README.md", REPO / "CHANGELOG.md", REPO / "AGENTS.md", *REPO.glob("docs/*.md"), *KIT.rglob("*.md")]:
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
    problems.append("kit/AGENTS.md has no '## This project' section (agd keeps everything from it down as the project's)")
marker = re.search(r"agentic-defaults (\d+\.\d+\.\d+)", agreement)
if not marker or marker.group(1) != version:
    problems.append(f"kit/AGENTS.md version marker doesn't match VERSION {version}")
# CHANGELOG.md holds at most one entry, for the unreleased VERSION; released versions are links
# under "## Released" to their GitHub releases (scripts/release.py moves an entry there).
changelog = (REPO / "CHANGELOG.md").read_text()
entries = re.findall(r"^## (\d+\.\d+\.\d+)([^\n]*)\n(.*?)(?=^## |\Z)", changelog, re.M | re.S)
for entry_version, entry_heading, _ in entries:
    if entry_version != version or entry_heading != " (unreleased)":
        problems.append(f"CHANGELOG.md: '## {entry_version}{entry_heading}' isn't the unreleased VERSION {version}; "
                        f"released versions belong under '## Released' as links")
released_links = set(re.findall(r"^- \[(\d+\.\d+\.\d+)\]\(https://github\.com/[^)\s]+/releases/tag/v\1\) "
                                r"\(\d{4}-\d{2}-\d{2}\)$", changelog, re.M))


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def check_unreleased_entry():
    entry = next((body for v, heading, body in entries if v == version and heading == " (unreleased)"), None)
    if entry is None:
        problems.append(f"CHANGELOG.md has no '## {version} (unreleased)' entry for VERSION {version}")
    elif not re.search(r"^- \S", entry, re.M):
        problems.append(f"CHANGELOG.md's {version} entry has no bullet points describing the change")
    elif "TODO" in entry:
        problems.append(f"CHANGELOG.md's {version} entry still has a TODO: describe the change")


# Release rule: once VERSION is tagged as released, any change to kit/ or packs.txt needs a new version.
tag = f"v{version}"
if git("rev-parse", "--git-dir").returncode != 0:
    release_note = "release rule skipped (not a git repository)"
    if version not in released_links:
        check_unreleased_entry()
elif git("rev-parse", "-q", "--verify", f"refs/tags/{tag}").returncode == 0:
    release_note = f"released as {tag}"
    if any(v == version for v, _, _ in entries):
        problems.append(f"CHANGELOG.md: {version} is released as {tag}, so its entry belongs in the GitHub release, "
                        f"not under '## {version}'")
    released = ("kit", "packs.txt")
    changed = sorted(set(git("diff", "--name-only", tag, "--", *released).stdout.splitlines())
                     | set(git("ls-files", "--others", "--exclude-standard", "--", *released).stdout.splitlines()))
    if changed:
        listed = ", ".join(changed[:3]) + (f" and {len(changed) - 3} more" if len(changed) > 3 else "")
        problems.append(f"kit/ or packs.txt changed since {tag} was released ({listed}). Start a new version with "
                        f"'bash scripts/bump.sh <version>': patch for wording and fixes, minor for new agents, "
                        f"skills or rules, major for renames or removals")
else:
    release_note = f"not released yet (no tag {tag})"
    check_unreleased_entry()

# Every released (tagged) version is linked under "## Released".
if git("rev-parse", "--git-dir").returncode == 0:
    for released in git("tag", "-l", "v*").stdout.split():
        if released[1:] not in released_links:
            problems.append(f"CHANGELOG.md: {released[1:]} is released as {released}, so '## Released' needs "
                            f"'- [{released[1:]}](https://github.com/<owner>/<repo>/releases/tag/{released}) (YYYY-MM-DD)'")

# packs.txt groups kit files into the packs agd installs. agd copies whole packs, keeps everything
# from "## This project" down as the project's, and splits packs.txt and its lock file on spaces.
if git("rev-parse", "--git-dir").returncode == 0:
    listed = git("ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "kit").stdout.split("\0")
    kit_files = sorted({p[len("kit/"):] for p in listed if p and (REPO / p).is_file()})
else:
    kit_files = sorted(p.relative_to(KIT).as_posix() for p in KIT.rglob("*") if p.is_file() and p.name != ".DS_Store")

packs_file = REPO / "packs.txt"
if not packs_file.exists():
    problems.append("packs.txt is missing: it lists the packs agd installs")
pack_paths, requires, min_agd, current = {}, {}, None, None
for number, line in enumerate(packs_file.read_text().splitlines() if packs_file.exists() else [], 1):
    words = line.split()
    if not words or words[0].startswith("#"):
        continue
    if line[0].isspace():
        if current and len(words) == 1:
            pack_paths[current].append(words[0])
            continue
    elif words[0] == "min-agd" and len(words) == 2 and re.fullmatch(r"\d+\.\d+\.\d+", words[1]):
        min_agd = words[1]
        continue
    elif (words[0] == "pack" and (len(words) == 2 or (len(words) > 3 and words[2] == "requires"))
          and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", words[1]) and words[1] not in pack_paths):
        current = words[1]
        pack_paths[current], requires[current] = [], words[3:]
        continue
    problems.append(f"packs.txt:{number}: expected 'min-agd <version>', 'pack <new-name> [requires <pack> ...]' "
                    f"or an indented kit path without spaces")


if min_agd is None:
    problems.append("packs.txt needs a 'min-agd <version>' line: the oldest agd (github.com/Zejnilovic/agd) "
                    "that can install this kit")

owners = {path: [] for path in kit_files}
for pack, paths in pack_paths.items():
    for entry in paths:
        matched = [path for path in kit_files if path == entry or (entry.endswith("/") and path.startswith(entry))]
        if not matched:
            problems.append(f"packs.txt: '{entry}' in pack '{pack}' matches no file in kit/")
        for path in matched:
            owners[path].append(pack)
for path, packs in owners.items():
    if not packs:
        problems.append(f"kit/{path} isn't in any pack: add it to packs.txt")
    elif len(packs) > 1:
        problems.append(f"kit/{path} is listed more than once in packs.txt ({', '.join(packs)}): keep it in one pack")
    if re.search(r"\s", path):
        problems.append(f"kit/{path}: kit paths can't contain whitespace (agd splits packs.txt and its lock on spaces)")
    if path != "AGENTS.md" and re.search(r"^## This project[ \t]*$", (KIT / path).read_text(errors="replace"), re.M):
        problems.append(f"kit/{path} has a '## This project' heading. Only kit/AGENTS.md may: in projects, "
                        f"agd keeps everything from that heading down as the project's")


def packs_of(folder):
    return {pack for path in kit_files if path.startswith(folder) for pack in owners[path]}


def required(pack):
    """Every pack that pack needs, directly or through others."""
    found, todo = set(), list(requires.get(pack, []))
    while todo:
        other = todo.pop()
        if other not in found:
            found.add(other)
            todo.extend(requires.get(other, []))
    return found


for pack, needed in requires.items():
    for other in needed:
        if other not in requires:
            problems.append(f"packs.txt: pack '{pack}' requires '{other}', which isn't a pack")
    if pack in required(pack):
        problems.append(f"packs.txt: pack '{pack}' requires itself through a cycle")

for skill in skills:
    split = sorted(packs_of(f".claude/skills/{skill}/"))
    if len(split) > 1:
        problems.append(f"kit/.claude/skills/{skill}/ is split across packs ({', '.join(split)}): "
                        f"a skill folder belongs to one pack")

for agent, preload in preloads.items():
    path = f".claude/agents/{agent}.md"
    if len(owners.get(path, [])) != 1:
        continue
    pack = owners[path][0]
    for skill in preload:
        outside = sorted(packs_of(f".claude/skills/{skill}/") - {pack} - required(pack))
        if outside:
            problems.append(f"kit/{path} preloads the '{skill}' skill from pack '{outside[0]}', "
                            f"which pack '{pack}' doesn't require")

# Only the kit's part counts: projects replace everything from "## This project" down with their own.
words = len(agreement.split("\n## This project", 1)[0].split())
if words > AGREEMENT_WORD_BUDGET:
    problems.append(f"kit/AGENTS.md has {words} words above 'This project', over the {AGREEMENT_WORD_BUDGET}-word budget")

# Kit-owned files say so, so agents in a project know not to edit them. Templates are exempt:
# agents copy them into new project files.
marked = [*AGENTS_DIR.glob("*.md"), *SKILLS_DIR.glob("*/SKILL.md"), *KIT.rglob("*.sh"),
          KIT / ".local_context/README.md", KIT / ".local_context/.gitignore", KIT / "AGENTS.md"]
for path in marked:
    if "From agentic-defaults" not in path.read_text()[:1500]:
        problems.append(f"{rel(path)}: missing the 'From agentic-defaults' marker near the top")

for path in KIT.rglob("*.json"):
    try:
        json.loads(path.read_text())
    except ValueError as error:
        problems.append(f"{rel(path)}: invalid JSON: {error}")

for script in [*KIT.rglob("*.sh"), *(REPO / "scripts").glob("*.sh")]:
    result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    if result.returncode != 0:
        problems.append(f"{rel(script)}: syntax error: {result.stderr.strip()}")

mermaid_files = [p for p in [REPO / "README.md", *REPO.glob("docs/*.md"), *KIT.rglob("*.md")]
                 if "```mermaid" in p.read_text()]
if os.environ.get("AGENTIC_DEFAULTS_SKIP_MERMAID"):
    mermaid_note = "Mermaid rendering skipped (AGENTIC_DEFAULTS_SKIP_MERMAID is set)"
elif shutil.which("mmdc"):
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
      f"kit/AGENTS.md at {words}/{AGREEMENT_WORD_BUDGET} words, version {version} {release_note}. {mermaid_note}.")
if problems:
    print("\nProblems:")
    for problem in problems:
        print(f"- {problem}")
    sys.exit(1)
print("No problems found.")
