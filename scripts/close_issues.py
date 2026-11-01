#!/usr/bin/env python3
"""Tells issues about a release. The Release workflow runs it; run it by hand to finish a failed run.

Reads the release notes for a marker at the end of each bullet: "(ref #20, ref #11, #12)" closes #12
and comments on #20 and #11, without closing them. Each issue gets one comment, listing the bullets
that name it. Safe to run again: an issue that already mentions this release gets no second comment.

Usage: python3 scripts/close_issues.py --version X.Y.Z --notes FILE [--repo OWNER/NAME] [--dry-run]
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

MARKER = re.compile(r"\s*\(((?:ref )?#\d+(?:, (?:ref )?#\d+)*)\)\s*$")
LOOKS_LIKE_MARKER = re.compile(r"\([^()]*#\d+[^()]*\)\s*$")
KEYWORD = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?):?\s+#\d+", re.I)


def bullets(text):
    """The text's bullets, with indented continuation lines joined."""
    found = []
    for line in text.splitlines():
        if line.startswith("- "):
            found.append(line[2:].strip())
        elif found and line[:1].isspace() and line.strip():
            found[-1] += " " + line.strip()
    return found


def marker_problems(text):
    """One message per bullet whose marker this script would misread."""
    problems = []
    for bullet in bullets(text):
        if KEYWORD.search(bullet):
            problems.append(f"'{KEYWORD.search(bullet).group()}': write the issue as a marker at the end of the "
                            f"bullet, such as (#12) or (ref #20, #12)")
        elif LOOKS_LIKE_MARKER.search(bullet) and not MARKER.search(bullet):
            problems.append(f"'{LOOKS_LIKE_MARKER.search(bullet).group().strip()}': a marker looks like (#12) or "
                            f"(ref #20, #12)")
    return problems


def parse(text):
    """{issue number: {"fixes": whether a bullet closes it, "bullets": the bullets naming it, markers removed}}"""
    issues = {}
    for bullet in bullets(text):
        marker = MARKER.search(bullet)
        if not marker:
            continue
        for item in marker.group(1).split(", "):
            issue = issues.setdefault(int(item.split("#")[1]), {"fixes": False, "bullets": []})
            issue["fixes"] = issue["fixes"] or not item.startswith("ref ")
            issue["bullets"].append(bullet[: marker.start()])
    return issues


def comment(issue, link):
    if issue["fixes"]:
        intro = f"Fixed in {link}. Run `agd update` in your project to get it."
    else:
        intro = f"{link} has a related change, which doesn't close this issue. Run `agd update` in your project to get it."
    return intro + "\n\nWhat changed:\n" + "".join(f"- {bullet}\n" for bullet in issue["bullets"])


def main():
    parser = argparse.ArgumentParser(description="Close and comment on the issues a release names.")
    parser.add_argument("--version", required=True, help="the released version, X.Y.Z")
    parser.add_argument("--notes", required=True, help="file with the release notes")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"),
                        help="GitHub repository as OWNER/NAME (default: $GITHUB_REPOSITORY)")
    parser.add_argument("--dry-run", action="store_true", help="check the issues and say what would happen")
    args = parser.parse_args()
    if not args.repo:
        parser.error("--repo is required when GITHUB_REPOSITORY isn't set")

    notes = pathlib.Path(args.notes).read_text()
    problems = marker_problems(notes)
    if problems:
        for problem in problems:
            print(f"problem: {problem}")
        sys.exit(1)

    issues = parse(notes)
    if not issues:
        print(f"No issues named in the notes for {args.version}.")
        return

    def gh(*command, stdin=None):
        return subprocess.run(["gh", "issue", *command, "--repo", args.repo], input=stdin, capture_output=True, text=True)

    url = f"https://github.com/{args.repo}/releases/tag/v{args.version}"
    failed = False
    for number, issue in sorted(issues.items()):
        viewed = gh("view", str(number), "--json", "state,url,comments")
        if viewed.returncode != 0:
            print(f"problem: #{number}: {viewed.stderr.strip()}")
            failed = True
            continue
        current = json.loads(viewed.stdout)
        if "/pull/" in current["url"]:
            print(f"problem: #{number} is a pull request, not an issue")
            failed = True
            continue
        commented = any(f"{url})" in entry["body"] for entry in current["comments"])
        closes = issue["fixes"] and current["state"] == "OPEN"
        if args.dry_run:
            if not commented:
                print(f"would comment on #{number}")
            if closes:
                print(f"would close #{number}")
            continue
        if not commented:
            done = gh("comment", str(number), "--body-file", "-", stdin=comment(issue, f"[{args.version}]({url})"))
            if done.returncode != 0:
                print(f"problem: #{number}: comment failed: {done.stderr.strip()}")
                failed = True
                continue
            print(f"commented on #{number}")
        if closes:
            done = gh("close", str(number), "--reason", "completed")
            if done.returncode != 0:
                print(f"problem: #{number}: close failed: {done.stderr.strip()}")
                failed = True
                continue
            print(f"closed #{number}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
