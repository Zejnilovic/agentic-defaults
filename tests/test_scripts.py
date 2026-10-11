"""Behavior tests for the kit's shell scripts. Run: python3 -m unittest discover -s tests"""

import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
KIT = REPO / "kit"
CONTEXT_CHECK = KIT / ".claude/skills/context-md/check.sh"
SURVEY = KIT / ".claude/skills/project-scan/survey.sh"
SYNC = REPO / "scripts/sync.sh"

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, env=GIT_ENV, capture_output=True, text=True)


def write(root, rel, text="x\n"):
    path = pathlib.Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class GitRepoCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        run(["git", "init", "-q", "-b", "main"], self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def commit(self, message="commit"):
        run(["git", "add", "-A"], self.root)
        result = run(["git", "commit", "-q", "-m", message], self.root)
        self.assertEqual(result.returncode, 0, result.stderr)


class ContextCheckTest(GitRepoCase):
    def setUp(self):
        super().setUp()
        write(self.root, "CONTEXT.md", "# Root\n")
        write(self.root, "backend/CONTEXT.md", "# Backend\n")
        write(self.root, "backend/api/orders.py")
        write(self.root, "backend/tests/test_orders.py")
        write(self.root, "scripts/deploy.sh")
        self.commit("initial")

    def check(self, *args):
        return run(["bash", str(CONTEXT_CHECK), *args], self.root)

    def test_flags_nearest_context_when_code_changes_without_it(self):
        write(self.root, "backend/api/orders.py", "changed\n")
        result = self.check()
        self.assertEqual(result.returncode, 0)
        self.assertIn("backend/CONTEXT.md", result.stdout)
        self.assertIn("backend/api/orders.py", result.stdout)
        self.assertNotIn("- CONTEXT.md", result.stdout)

    def test_strict_fails_only_when_something_to_check(self):
        write(self.root, "backend/api/orders.py", "changed\n")
        self.assertEqual(self.check("--strict").returncode, 1)
        write(self.root, "backend/CONTEXT.md", "# Backend, updated\n")
        self.assertEqual(self.check("--strict").returncode, 0)

    def test_updated_context_is_not_flagged(self):
        write(self.root, "backend/api/orders.py", "changed\n")
        write(self.root, "backend/CONTEXT.md", "# Backend, updated\n")
        self.assertNotIn("backend/CONTEXT.md:", self.check().stdout)

    def test_test_and_doc_only_changes_are_ignored(self):
        write(self.root, "backend/tests/test_orders.py", "changed\n")
        write(self.root, "docs/guide.md", "new guide\n")
        result = self.check("--strict")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_housekeeping_files_are_ignored(self):
        for rel in [".gitignore", "LICENSE", "VERSION", "CHANGELOG", ".editorconfig"]:
            write(self.root, rel, "changed\n")
        result = self.check("--strict")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_code_outside_areas_maps_to_root(self):
        write(self.root, "scripts/deploy.sh", "changed\n")
        self.assertIn("- CONTEXT.md", self.check().stdout)

    def test_new_untracked_file_counts(self):
        write(self.root, "backend/api/invoices.py", "new\n")
        self.assertIn("backend/api/invoices.py", self.check().stdout)

    def test_base_ref_includes_committed_branch_changes(self):
        run(["git", "checkout", "-q", "-b", "feature"], self.root)
        write(self.root, "backend/api/orders.py", "changed on branch\n")
        self.commit("feature work")
        self.assertNotIn("backend/CONTEXT.md", self.check().stdout)
        self.assertIn("backend/CONTEXT.md", self.check("--base", "main").stdout)

    def test_reports_code_with_no_context_at_all(self):
        os.remove(os.path.join(self.root, "CONTEXT.md"))
        self.commit("drop root context")
        write(self.root, "scripts/deploy.sh", "changed\n")
        self.assertIn("No CONTEXT.md covers", self.check().stdout)


class SyncTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.project = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def sync(self, *args):
        return run(["bash", str(SYNC), self.project, *args], REPO)

    def test_report_lists_missing_files_and_changes_nothing(self):
        result = self.sync()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("missing", result.stdout)
        self.assertIn(".claude/skills/tdd/SKILL.md", result.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.project, "AGENTS.md")))

    def test_apply_copies_everything_then_reports_in_sync(self):
        self.assertEqual(self.sync("--apply").returncode, 0)
        for rel in ["AGENTS.md", "CLAUDE.md", ".local_context/.gitignore", ".claude/agents/developer.md",
                    ".claude/skills/project-scan/survey.sh"]:
            self.assertTrue(os.path.exists(os.path.join(self.project, rel)), rel)
        self.assertIn("0 differ, 0 missing, 0 to merge by hand", self.sync().stdout)

    def test_apply_updates_agreement_but_keeps_this_project_section(self):
        write(self.project, "AGENTS.md", "# Old agreement\n\nold rule\n\n## This project\n\n- Test: `make test`\n")
        result = self.sync("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = pathlib.Path(self.project, "AGENTS.md").read_text()
        self.assertNotIn("old rule", text)
        self.assertIn("## Deliver", text)
        self.assertIn("- Test: `make test`", text)
        self.assertEqual(text.count("## This project"), 1)

    def test_never_overwrites_custom_claude_md(self):
        write(self.project, "CLAUDE.md", "@AGENTS.md\n\nExtra local rule\n")
        result = self.sync("--apply")
        self.assertIn("CLAUDE.md", result.stdout)
        self.assertIn("by hand", result.stdout)
        self.assertIn("Extra local rule", pathlib.Path(self.project, "CLAUDE.md").read_text())

    def test_agreement_without_this_project_section_is_left_alone(self):
        write(self.project, "AGENTS.md", "# Our own rules\n")
        self.sync("--apply")
        self.assertEqual(pathlib.Path(self.project, "AGENTS.md").read_text(), "# Our own rules\n")

    def test_existing_only_updates_without_adding(self):
        write(self.project, ".claude/skills/tdd/SKILL.md", "outdated\n")
        self.sync("--apply", "--existing-only")
        self.assertNotEqual(pathlib.Path(self.project, ".claude/skills/tdd/SKILL.md").read_text(), "outdated\n")
        self.assertFalse(os.path.exists(os.path.join(self.project, ".claude/agents/developer.md")))


class VersionTest(GitRepoCase):
    """check.py's release rule and scripts/bump.sh, on a copy of this repo released as 1.0.0."""

    def setUp(self):
        super().setUp()
        shutil.copytree(REPO, self.root, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.set_release("1.0.0", "## 1.0.0 (2026-01-01)\n\n- First release.\n")

    def set_release(self, version, entry):
        write(self.root, "VERSION", version + "\n")
        agreement = pathlib.Path(self.root, "kit/AGENTS.md")
        agreement.write_text(re.sub(r"agentic-defaults \d+\.\d+\.\d+", f"agentic-defaults {version}",
                                    agreement.read_text(), count=1))
        changelog = pathlib.Path(self.root, "CHANGELOG.md")
        intro = changelog.read_text().split("\n## ", 1)[0]
        changelog.write_text(f"{intro}\n{entry}")
        self.commit("release")
        run(["git", "tag", "-f", f"v{version}"], self.root)

    def check(self):
        env = {**GIT_ENV, "AGENTIC_DEFAULTS_SKIP_MERMAID": "1"}
        return subprocess.run(["python3", "scripts/check.py"], cwd=self.root, env=env, capture_output=True, text=True)

    def bump(self, version):
        return run(["bash", "scripts/bump.sh", version], self.root)

    def read(self, rel):
        return pathlib.Path(self.root, rel).read_text()

    def test_released_version_with_unchanged_kit_passes(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_kit_change_after_release_fails_until_bumped_and_described(self):
        write(self.root, "kit/.claude/skills/tdd/SKILL.md", self.read("kit/.claude/skills/tdd/SKILL.md") + "\nNew rule.\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("v1.0.0", result.stdout)
        self.assertIn("bump.sh", result.stdout)

        self.assertEqual(self.bump("1.0.1").returncode, 0)
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("TODO", result.stdout)

        write(self.root, "CHANGELOG.md", self.read("CHANGELOG.md").replace("TODO: describe the change", "New TDD rule."))
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_new_untracked_kit_file_counts_as_a_change(self):
        write(self.root, "kit/.claude/skills/tdd/notes.md", "extra\n")
        self.assertEqual(self.check().returncode, 1)

    def test_changes_outside_kit_need_no_bump(self):
        write(self.root, "README.md", self.read("README.md") + "\nMore words.\n")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_released_version_needs_a_dated_heading(self):
        self.set_release("1.0.0", "## 1.0.0 (unreleased)\n\n- First release.\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("date", result.stdout)

    def test_bump_updates_version_marker_and_changelog(self):
        result = self.bump("1.1.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read("VERSION"), "1.1.0\n")
        self.assertIn("agentic-defaults 1.1.0", self.read("kit/AGENTS.md").splitlines()[0])
        changelog = self.read("CHANGELOG.md")
        self.assertLess(changelog.index("## 1.1.0 (unreleased)"), changelog.index("## 1.0.0 (2026-01-01)"))

    def test_bump_rejects_malformed_or_not_greater_versions(self):
        for bad in ["1.0", "v1.0.1", "1.0.0", "0.9.9"]:
            result = self.bump(bad)
            self.assertNotEqual(result.returncode, 0, bad)
        self.assertEqual(self.read("VERSION"), "1.0.0\n")


class SurveyTest(unittest.TestCase):
    def test_runs_on_this_repository(self):
        result = run(["bash", str(SURVEY), str(REPO)], REPO)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Survey:", result.stdout)
        self.assertIn("## Docs and AI context", result.stdout)


if __name__ == "__main__":
    unittest.main()
