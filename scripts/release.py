#!/usr/bin/env python3
"""Releases the unreleased version in CHANGELOG.md. The Release workflow runs it; run it by hand
only to try it out.

Writes the entry's text to the notes file (relative links made absolute for the tag), replaces the
entry with a link to the GitHub release under "## Released", and prints the version. Committing,
tagging and creating the GitHub release are left to the caller.

Usage: python3 scripts/release.py --notes FILE [--repo OWNER/NAME] [--date YYYY-MM-DD]
"""

import argparse
import datetime
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def fail(message):
    print(f"release.py: {message}", file=sys.stderr)
    sys.exit(1)


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def origin_slug():
    url = git("remote", "get-url", "origin").stdout.strip()
    match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    return match.group(1) if match else None


parser = argparse.ArgumentParser(description="Release the unreleased version in CHANGELOG.md.")
parser.add_argument("--notes", required=True, help="file to write the release notes to")
parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY") or origin_slug(),
                    help="GitHub repository as OWNER/NAME (default: $GITHUB_REPOSITORY or the origin remote)")
parser.add_argument("--date", default=datetime.date.today().isoformat(), help="release date (default: today)")
args = parser.parse_args()

if not args.repo or not re.fullmatch(r"[\w.-]+/[\w.-]+", args.repo):
    fail(f"--repo must look like OWNER/NAME, got: {args.repo}")
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
    fail(f"--date must look like YYYY-MM-DD, got: {args.date}")

version = (REPO / "VERSION").read_text().strip()
tag = f"v{version}"
if git("rev-parse", "-q", "--verify", f"refs/tags/{tag}").returncode == 0:
    fail(f"{version} is already released as {tag}. Start a new version with 'bash scripts/bump.sh <version>'.")

changelog_path = REPO / "CHANGELOG.md"
changelog = changelog_path.read_text()
entry = re.search(rf"^## {re.escape(version)} \(unreleased\)\n(.*?)(?=^## |\Z)", changelog, re.M | re.S)
if not entry:
    fail(f"CHANGELOG.md has no '## {version} (unreleased)' entry to release.")
body = entry.group(1).strip()
if not re.search(r"^- \S", body, re.M):
    fail(f"CHANGELOG.md's {version} entry has no bullet points describing the change.")
if "TODO" in body:
    fail(f"CHANGELOG.md's {version} entry still has a TODO: describe the change.")

# Release notes are read on GitHub, where links relative to the repository root don't resolve.
notes = re.sub(r"\]\((?![a-z]+:|#)([^)\s]+)\)", rf"](https://github.com/{args.repo}/blob/{tag}/\1)", body)
pathlib.Path(args.notes).write_text(notes + "\n")

link = f"- [{version}](https://github.com/{args.repo}/releases/tag/{tag}) ({args.date})"
changelog = changelog[: entry.start()] + changelog[entry.end():]
if re.search(r"^## Released\n", changelog, re.M):
    changelog = re.sub(r"^## Released\n\n?", f"## Released\n\n{link}\n", changelog, count=1, flags=re.M)
else:
    changelog = changelog.rstrip("\n") + f"\n\n## Released\n\n{link}\n"
changelog_path.write_text(changelog)

print(version)
