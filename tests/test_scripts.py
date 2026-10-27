"""Behavior tests for the kit's shell scripts. Run: python3 -m unittest discover -s tests"""

import json
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
STATS = KIT / ".claude/skills/session-retro/stats.sh"

GIT_ENV = {
    **os.environ,
    # Ignore the user's and the system's git settings, such as signed tags.
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
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

    # Hook mode speaks the JSON both Claude Code (Stop) and GitHub Copilot (agentStop) accept:
    # exit 0, and {"decision": "block", "reason": ...} on stdout to make the agent continue.
    def hook(self, stdin='{"hook_event_name": "Stop", "stop_hook_active": false}'):
        result = subprocess.run(["bash", str(CONTEXT_CHECK), "--hook"], cwd=self.root, env=GIT_ENV,
                                input=stdin, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def test_hook_blocks_once_with_the_files_to_check(self):
        write(self.root, "backend/api/orders.py", "changed\n")
        output = self.hook()
        self.assertEqual(output["decision"], "block")
        self.assertIn("backend/CONTEXT.md", output["reason"])
        self.assertEqual(self.hook(), {}, "the same finding must not block twice")

    def test_hook_blocks_again_when_the_finding_changes(self):
        write(self.root, "backend/api/orders.py", "changed\n")
        self.assertEqual(self.hook()["decision"], "block")
        write(self.root, "scripts/deploy.sh", "changed\n")
        self.assertEqual(self.hook()["decision"], "block")

    def test_hook_never_blocks_a_continuation(self):
        write(self.root, "backend/api/orders.py", "changed\n")
        self.assertEqual(self.hook('{"hookEventName": "agentStop", "stop_hook_active": true}'), {})

    def test_hook_passes_when_nothing_to_check(self):
        self.assertEqual(self.hook(), {})

    def test_hook_reason_is_valid_json_with_awkward_paths(self):
        write(self.root, 'backend/api/say "hi"\\now.py', "new\n")
        self.assertIn("backend/CONTEXT.md", self.hook()["reason"])

    def test_reports_code_with_no_context_at_all(self):
        os.remove(os.path.join(self.root, "CONTEXT.md"))
        self.commit("drop root context")
        write(self.root, "scripts/deploy.sh", "changed\n")
        self.assertIn("No CONTEXT.md covers", self.check().stdout)

    # Files that agd installs belong to their source, not to the project; .agd.lock lists them.
    def install_kit(self, *paths, lock_only=()):
        lines = ["agd-lock 1", "source kit https://example.com/kit.git 1.0.0", "pack kit core"]
        for rel in paths:
            write(self.root, rel, "kit\n")
        for rel in (*paths, *lock_only):
            lines.append(f"file kit {rel} 0123456789abcdef0123456789abcdef01234567")
        write(self.root, ".agd.lock", "\n".join(lines) + "\n")

    def test_kit_update_needs_no_context_change(self):
        self.install_kit(".claude/skills/context-md/check.sh", ".github/hooks/context-check.json")
        self.commit("install kit")
        self.install_kit(".claude/skills/context-md/check.sh", ".github/hooks/context-check.json",
                         ".claude/skills/session-retro/stats.sh")
        write(self.root, ".claude/skills/context-md/check.sh", "kit, updated\n")
        result = self.check("--strict")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("No CONTEXT.md covers", result.stdout)
        self.assertEqual(self.hook(), {})

    def test_removed_kit_files_are_skipped_with_base(self):
        self.install_kit(".claude/skills/context-md/check.sh", ".claude/skills/terraform/plan.sh")
        self.commit("install kit")
        run(["git", "checkout", "-q", "-b", "remove-pack"], self.root)
        os.remove(os.path.join(self.root, ".claude/skills/terraform/plan.sh"))
        self.install_kit(".claude/skills/context-md/check.sh")
        self.commit("agd remove terraform")
        result = self.check("--strict", "--base", "main")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_project_files_next_to_kit_files_are_still_flagged(self):
        self.install_kit(".claude/skills/context-md/check.sh")
        self.commit("install kit")
        write(self.root, ".claude/skills/own-skill/run.sh", "ours\n")
        write(self.root, ".claude/skills/context-md/check.sh", "kit, updated\n")
        result = self.check("--strict")
        self.assertEqual(result.returncode, 1)
        self.assertIn(".claude/skills/own-skill/run.sh", result.stdout)
        self.assertNotIn("context-md/check.sh", result.stdout)

    def test_mixed_change_flags_only_project_code(self):
        self.install_kit(".claude/skills/context-md/check.sh")
        self.commit("install kit")
        write(self.root, ".claude/skills/context-md/check.sh", "kit, updated\n")
        write(self.root, "backend/api/orders.py", "changed\n")
        result = self.check()
        self.assertIn("- backend/CONTEXT.md: backend/api/orders.py", result.stdout)
        self.assertNotIn("- CONTEXT.md", result.stdout)
        self.assertNotIn(".agd.lock", result.stdout)


class SyncStubTest(unittest.TestCase):
    """scripts/sync.sh is replaced by agd: it only points there."""

    def test_points_to_agd_adopt_and_changes_nothing(self):
        with tempfile.TemporaryDirectory() as project:
            result = run(["bash", str(SYNC), project, "--apply"], REPO)
            self.assertEqual(result.returncode, 2)
            self.assertIn("agd", result.stderr)
            self.assertIn(f"agd -C {project} adopt", result.stderr)
            self.assertEqual(os.listdir(project), [])


RELEASED_1_0_0 = "## Released\n\n- [1.0.0](https://github.com/example/kit/releases/tag/v1.0.0) (2026-01-01)\n"


class VersionTest(GitRepoCase):
    """check.py's release rule, scripts/bump.sh and scripts/release.py, on a copy of this repo released as 1.0.0."""

    def setUp(self):
        super().setUp()
        shutil.copytree(REPO, self.root, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.set_release("1.0.0", RELEASED_1_0_0)

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

    def release(self):
        return run(["python3", "scripts/release.py", "--repo", "example/kit", "--date", "2026-02-02",
                    "--notes", "notes.md"], self.root)

    def describe(self, text):
        write(self.root, "CHANGELOG.md", self.read("CHANGELOG.md").replace("TODO: describe the change", text))

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

        self.describe("New TDD rule.")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_new_untracked_kit_file_counts_as_a_change(self):
        write(self.root, "kit/.claude/skills/tdd/notes.md", "extra\n")
        self.assertEqual(self.check().returncode, 1)

    def test_packs_change_after_release_needs_a_new_version(self):
        write(self.root, "packs.txt", self.read("packs.txt") + "# Regrouped\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("packs.txt", result.stdout)
        self.assertIn("bump.sh", result.stdout)

    def test_changes_outside_kit_need_no_bump(self):
        write(self.root, "README.md", self.read("README.md") + "\nMore words.\n")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_released_version_cannot_keep_an_unreleased_entry(self):
        self.set_release("1.0.0", "## 1.0.0 (unreleased)\n\n- First release.\n\n" + RELEASED_1_0_0)
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("1.0.0", result.stdout)

    def test_every_tag_is_listed_as_released(self):
        self.set_release("1.0.0", "## Released\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("v1.0.0", result.stdout)

    def test_unreleased_version_needs_its_entry(self):
        write(self.root, "VERSION", "1.1.0\n")
        write(self.root, "kit/AGENTS.md", self.read("kit/AGENTS.md").replace("agentic-defaults 1.0.0", "agentic-defaults 1.1.0", 1))
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("1.1.0 (unreleased)", result.stdout)

    def test_release_moves_notes_out_and_links_the_release(self):
        self.assertEqual(self.bump("1.1.0").returncode, 0)
        self.describe("New rule, see [the methodology](docs/methodology.md#principles).\n\nManual steps:\n\n- Do this")
        result = self.release()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "1.1.0")

        notes = self.read("notes.md")
        self.assertTrue(notes.startswith("- New rule"), notes)
        self.assertIn("(https://github.com/example/kit/blob/v1.1.0/docs/methodology.md#principles)", notes)
        self.assertIn("- Do this", notes)

        changelog = self.read("CHANGELOG.md")
        self.assertNotIn("## 1.1.0", changelog)
        self.assertNotIn("New rule", changelog)
        link = "- [1.1.0](https://github.com/example/kit/releases/tag/v1.1.0) (2026-02-02)"
        self.assertLess(changelog.index(link), changelog.index("- [1.0.0]"))

        os.remove(os.path.join(self.root, "notes.md"))
        self.commit("release 1.1.0")
        run(["git", "tag", "v1.1.0"], self.root)
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_release_refuses_without_a_described_unreleased_version(self):
        before = self.read("CHANGELOG.md")
        self.assertNotEqual(self.release().returncode, 0)
        self.assertEqual(self.bump("1.1.0").returncode, 0)
        after_bump = self.read("CHANGELOG.md")
        result = self.release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TODO", result.stderr)
        self.assertEqual(self.read("CHANGELOG.md"), after_bump)
        self.assertNotEqual(before, after_bump)

    def test_bump_updates_version_marker_and_changelog(self):
        result = self.bump("1.1.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read("VERSION"), "1.1.0\n")
        self.assertIn("agentic-defaults 1.1.0", self.read("kit/AGENTS.md").splitlines()[0])
        changelog = self.read("CHANGELOG.md")
        self.assertLess(changelog.index("## 1.1.0 (unreleased)"), changelog.index("## Released"))

    def test_bump_rejects_malformed_or_not_greater_versions(self):
        for bad in ["1.0", "v1.0.1", "1.0.0", "0.9.9"]:
            result = self.bump(bad)
            self.assertNotEqual(result.returncode, 0, bad)
        self.assertEqual(self.read("VERSION"), "1.0.0\n")


class CheckCopyCase(unittest.TestCase):
    """Runs check.py on a copy of this repo outside git."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        shutil.copytree(REPO, self.root, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def tearDown(self):
        self._tmp.cleanup()

    def check(self):
        env = {**os.environ, "AGENTIC_DEFAULTS_SKIP_MERMAID": "1"}
        return subprocess.run(["python3", "scripts/check.py"], cwd=self.root, env=env, capture_output=True, text=True)

    def read(self, rel):
        return pathlib.Path(self.root, rel).read_text()

    def assert_fails(self, *expected):
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stdout)
        for text in expected:
            self.assertIn(text, result.stdout)


class CheckBudgetTest(CheckCopyCase):
    def test_only_the_kit_part_of_the_agreement_counts(self):
        agreement, filler = "kit/AGENTS.md", " word" * 200 + "\n"
        write(self.root, agreement, self.read(agreement) + filler)
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

        write(self.root, agreement, self.read(agreement).replace("\n## This project", filler + "\n## This project", 1))
        self.assert_fails("budget")


class CheckPacksTest(CheckCopyCase):
    """check.py's packs.txt rules."""

    def edit_packs(self, old, new):
        packs = self.read("packs.txt")
        self.assertIn(old, packs)
        write(self.root, "packs.txt", packs.replace(old, new, 1))

    def test_kit_as_shipped_passes(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_kit_file_in_no_pack_fails(self):
        write(self.root, "kit/extra.txt")
        self.assert_fails("kit/extra.txt", "packs.txt")

    def test_kit_file_in_two_packs_fails(self):
        self.edit_packs("pack flask requires core\n", "pack flask requires core\n  .claude/skills/tdd/\n")
        self.assert_fails("kit/.claude/skills/tdd/SKILL.md", "core, flask")

    def test_entry_matching_no_kit_file_fails(self):
        self.edit_packs("pack flask requires core\n", "pack flask requires core\n  .claude/agents/ghost.md\n")
        self.assert_fails(".claude/agents/ghost.md", "matches no file")

    def test_unknown_required_pack_fails(self):
        self.edit_packs("pack flask requires core", "pack flask requires core vue")
        self.assert_fails("'vue'")

    def test_required_packs_cannot_form_a_cycle(self):
        self.edit_packs("pack core\n", "pack core requires flask\n")
        self.assert_fails("cycle")

    def test_agent_preloading_a_skill_outside_its_packs_fails(self):
        self.edit_packs("pack flask requires core", "pack flask")
        self.assert_fails("kit/.claude/agents/flask-developer.md", "'implementation'")

    def test_skill_folder_split_across_packs_fails(self):
        self.edit_packs("  .claude/skills/project-scan/\n",
                        "  .claude/skills/project-scan/SKILL.md\n  .claude/skills/project-scan/Makefile.template\n")
        self.edit_packs("pack copilot-hook requires core\n",
                        "pack copilot-hook requires core\n  .claude/skills/project-scan/survey.sh\n")
        self.assert_fails("kit/.claude/skills/project-scan/", "split")

    def test_whitespace_in_a_kit_path_fails(self):
        write(self.root, "kit/.claude/skills/tdd/my notes.md")
        self.assert_fails("kit/.claude/skills/tdd/my notes.md", "whitespace")

    def test_this_project_heading_only_in_the_agreement(self):
        tester = "kit/.claude/agents/tester.md"
        write(self.root, tester, self.read(tester) + "\n## This project\n\n- Extra rule.\n")
        self.assert_fails(tester, "## This project")

    def test_min_agd_is_required_and_a_version(self):
        line = re.search(r"^min-agd \S+$", self.read("packs.txt"), re.M).group(0)
        self.edit_packs(line, "min-agd 0.1")
        self.assert_fails("packs.txt:")
        self.edit_packs("min-agd 0.1\n", "")
        self.assert_fails("min-agd")

    def test_malformed_line_fails(self):
        self.edit_packs("pack core\n", "pack core\nflask-stuff\n")
        self.assert_fails("packs.txt:")


class SurveyTest(GitRepoCase):
    def test_lists_contract_files(self):
        write(self.root, "api/openapi.yaml", "openapi: 3.1.0\n")
        write(self.root, "proto/orders.proto", "syntax = \"proto3\";\n")
        write(self.root, "src/app.py", "x\n")
        result = run(["bash", str(SURVEY), self.root], self.root)
        self.assertIn("## Contracts", result.stdout)
        self.assertIn("api/openapi.yaml", result.stdout)
        self.assertIn("proto/orders.proto", result.stdout)

    def test_counts_recent_contributors_without_naming_them(self):
        write(self.root, "a.py", "x\n")
        self.commit("first")
        write(self.root, "b.py", "y\n")
        run(["git", "add", "-A"], self.root)
        run(["git", "-c", "user.name=Other", "-c", "user.email=other@example.com", "commit", "-q",
             "--author=Other <other@example.com>", "-m", "second"], self.root)
        result = run(["bash", str(SURVEY), self.root], self.root)
        self.assertIn("- Contributors, last 12 months: 2", result.stdout)
        self.assertNotIn("other@example.com", result.stdout)

    def test_lists_infrastructure_files(self):
        write(self.root, "infra/root.hcl", "remote_state {}\n")
        write(self.root, "infra/dev/vpc/terragrunt.hcl", "include \"root\" {}\n")
        write(self.root, "infra/modules/.terraform.lock.hcl", "provider {}\n")
        write(self.root, ".tflint.hcl", "plugin {}\n")
        write(self.root, ".pre-commit-config.yaml", "repos: []\n")
        write(self.root, "Procfile", "web: gunicorn app:app\n")
        result = run(["bash", str(SURVEY), self.root], self.root)
        build = result.stdout.split("## Build, dependency, runtime and CI files", 1)[1].split("\n## ", 1)[0]
        for path in ("infra/root.hcl", "infra/dev/vpc/terragrunt.hcl", "infra/modules/.terraform.lock.hcl",
                     ".tflint.hcl", ".pre-commit-config.yaml", "Procfile"):
            self.assertIn(f"- {path}\n", build)

    def test_reports_missing_standard_commands(self):
        write(self.root, "Makefile", "test:\n\tpytest\nlint:\n\truff .\n")
        result = run(["bash", str(SURVEY), self.root], self.root)
        self.assertIn("Missing standard make targets: setup run build format check", result.stdout)

    def test_runs_on_this_repository(self):
        result = run(["bash", str(SURVEY), str(REPO)], REPO)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Survey:", result.stdout)
        self.assertIn("## Docs and AI context", result.stdout)


def assistant(msg_id, model, tools=(), usage=None, ts="2026-10-25T10:00:00.000Z", sidechain=False):
    content = [{"type": "tool_use", "id": f"{msg_id}-{i}", "name": name, "input": {}} for i, name in enumerate(tools)]
    return {"type": "assistant", "timestamp": ts, "isSidechain": sidechain,
            "message": {"id": msg_id, "model": model, "content": content or [{"type": "text", "text": "ok"}],
                        "usage": usage or {"input_tokens": 10, "output_tokens": 100,
                                           "cache_read_input_tokens": 1000, "cache_creation_input_tokens": 50}}}


def user(content, ts="2026-10-25T10:00:00.000Z", **extra):
    return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": content}, **extra}


def tool_result(error=False, decision="accept"):
    return user([{"type": "tool_result", "tool_use_id": "t", "content": "output", "is_error": error}],
                permissionDecision={"decision": decision})


SESSION = [
    {"type": "custom-title", "customTitle": "x"},
    user("Please add the SECRET-TEXT export", ts="2026-10-25T10:00:00.000Z"),
    # One API call is logged once per content block: same message id, counted once.
    assistant("m1", "claude-sonnet-5-5", tools=["Bash"]),
    assistant("m1", "claude-sonnet-5-5", tools=["Edit"]),
    tool_result(),
    tool_result(error=True),
    assistant("m2", "claude-sonnet-5-5", tools=["Bash"]),
    tool_result(decision="reject"),
    user([{"type": "text", "text": "[Request interrupted by user for tool use]"}]),
    user("<command-name>/model</command-name>"),
    user("Caveat: generated", isMeta=True),
    user([{"type": "text", "text": "<ide_opened_file>a.py</ide_opened_file>"}, {"type": "text", "text": "Now fix it"}]),
    assistant("m3", "claude-sonnet-5-5", ts="2026-10-25T10:30:00.000Z"),
    "not json at all",
]
SUBAGENT = [
    user("Find the files", isSidechain=True),
    assistant("s1", "claude-haiku-5-5", tools=["Grep"], sidechain=True,
              usage={"input_tokens": 1, "output_tokens": 20, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}),
]


class StatsTest(GitRepoCase):
    """session-retro's stats.sh: counts from Claude Code's local session files, never their text."""

    def setUp(self):
        super().setUp()
        self._config = tempfile.TemporaryDirectory()
        self.config = pathlib.Path(self._config.name)
        self.session_id = "11111111-2222-3333-4444-555555555555"
        # Claude Code names a project's folder after its path, so it starts with "-".
        self.folder = self.config / "projects" / re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(self.root))
        self.write_session(self.folder / f"{self.session_id}.jsonl", SESSION)
        self.write_session(self.folder / self.session_id / "subagents" / "agent-a1.jsonl", SUBAGENT)

    def tearDown(self):
        self._config.cleanup()
        super().tearDown()

    def write_session(self, path, events):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join((e if isinstance(e, str) else json.dumps(e)) + "\n" for e in events))

    def stats(self, *args, env=None, session_id=None):
        env = {**GIT_ENV, "CLAUDE_CONFIG_DIR": str(self.config), **(env or {})}
        env.pop("CLAUDE_CODE_SESSION_ID", None)
        if session_id:
            env["CLAUDE_CODE_SESSION_ID"] = session_id
        return subprocess.run(["bash", str(STATS), *args], cwd=self.root, env=env, capture_output=True, text=True)

    @unittest.skipUnless(shutil.which("jq"), "needs jq")
    def test_counts_one_session_and_its_subagents(self):
        result = self.stats(session_id=self.session_id)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn(f"- Session: {self.session_id} (CLAUDE_CODE_SESSION_ID)", out)
        self.assertIn("- Time: 30 min", out)
        self.assertIn("- Models: claude-sonnet-5-5 (3 calls), claude-haiku-5-5 (1 calls)", out)
        self.assertIn("- Tokens: input 31, output 320, cache read 3000, cache write 150", out)
        self.assertIn("- Prompts: 2, interrupts: 1, denied tool calls: 1", out)
        self.assertIn("- Tool calls: 4, failed: 1 (Bash 2, Edit 1, Grep 1)", out)
        self.assertIn("- Subagents: 1", out)

    @unittest.skipUnless(shutil.which("jq"), "needs jq")
    def test_never_prints_session_text(self):
        result = self.stats(session_id=self.session_id)
        self.assertNotIn("SECRET-TEXT", result.stdout + result.stderr)
        self.assertNotIn("fix it", result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("jq"), "needs jq")
    def test_without_session_id_takes_the_newest_session_of_this_folder(self):
        older = self.folder / "00000000-0000-0000-0000-000000000000.jsonl"
        self.write_session(older, [assistant("o1", "claude-opus-5-5")])
        os.utime(older, (1, 1))
        result = self.stats()
        self.assertIn(f"- Session: {self.session_id} (newest for this folder", result.stdout)
        self.assertIn("claude-sonnet-5-5", result.stdout)

    @unittest.skipUnless(shutil.which("jq"), "needs jq")
    def test_takes_a_session_file_as_argument(self):
        other = self.config / "elsewhere.jsonl"
        self.write_session(other, [assistant("o1", "claude-opus-5-5")])
        result = self.stats(str(other), session_id=self.session_id)
        self.assertIn("- Models: claude-opus-5-5 (1 calls)", result.stdout)

    def test_reports_no_session_and_still_counts_git(self):
        shutil.rmtree(self.config / "projects")
        write(self.root, "a.py", "one\n")
        self.commit()
        write(self.root, "a.py", "one\ntwo\nthree\n")
        write(self.root, "b.py", "new\n")
        result = self.stats()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No Claude Code session found", result.stdout)
        self.assertIn("- Uncommitted: 1 changed files (+2 -0), 1 new files", result.stdout)

    def test_without_jq_says_so_and_still_counts_git(self):
        # A PATH with the tools the script needs, but no jq.
        bin_dir = pathlib.Path(self._config.name) / "bin"
        bin_dir.mkdir()
        for tool in ("bash", "git", "ls", "head", "sed", "awk", "tr", "cat", "basename", "dirname", "wc", "sort", "mktemp", "rm", "tail"):
            if shutil.which(tool):
                (bin_dir / tool).symlink_to(shutil.which(tool))
        result = self.stats(session_id=self.session_id, env={"PATH": str(bin_dir)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not shown: install jq", result.stdout)
        self.assertIn("- Uncommitted:", result.stdout)

    @unittest.skipUnless(shutil.which("jq"), "needs jq")
    def test_counts_commits_since_the_session_started(self):
        # The fixture session runs from 10:00 to 10:30 UTC on 2026-10-25.
        for name, when in (("before.py", "2026-10-25T09:00:00Z"), ("during.py", "2026-10-25T10:15:00Z")):
            write(self.root, name)
            run(["git", "add", "-A"], self.root)
            subprocess.run(["git", "commit", "-q", "-m", name], cwd=self.root, capture_output=True,
                           env={**GIT_ENV, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when})
        result = self.stats(session_id=self.session_id)
        self.assertIn("- Commits since the session started: 1 (+1 -0)", result.stdout)

    @unittest.skipUnless(shutil.which("jq"), "needs jq")
    def test_prompts_lists_only_what_the_user_typed(self):
        session = self.config / "prompts.jsonl"
        self.write_session(session, SESSION[:-2] + [user("line one\nline two " + "y" * 400)])
        result = self.stats("--prompts", str(session))
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertIn("1. Please add the SECRET-TEXT export", lines)
        self.assertIn("2. Now fix it", lines)
        self.assertTrue(lines[-1].startswith("3. line one line two yyy"), lines[-1])
        self.assertTrue(lines[-1].endswith("…") and len(lines[-1]) < 320, lines[-1])
        self.assertNotIn("Request interrupted", result.stdout)
        self.assertNotIn("/model", result.stdout)
        self.assertNotIn("Caveat", result.stdout)

    def write_log(self, rows):
        header = "date\ttask\tverdict\tprompts\tcorrections\ttool_calls\toutput_tokens\tcache_read_tokens\tlines_changed\n"
        body = "".join(f"2026-10-0{i + 1}\ttask{i}\twent well\t3\t0\t{calls}\t{tokens}\t1000\t20\n"
                       for i, (calls, tokens) in enumerate(rows))
        write(self.root, ".local_context/feedback/log.tsv", header + body)

    def test_baseline_is_the_median_of_earlier_retros(self):
        self.write_log([(2, 100), (50, 900), (4, 300)])
        result = self.stats(session_id=self.session_id)
        self.assertIn("- Usual for this project (median of the last 3 retros): output tokens 300, tool calls 4",
                      result.stdout)

    def test_no_baseline_before_three_retros(self):
        self.write_log([(2, 100), (4, 300)])
        result = self.stats(session_id=self.session_id)
        self.assertIn("- Usual for this project: no baseline yet (fewer than 3 retros in .local_context/feedback/log.tsv)",
                      result.stdout)


if __name__ == "__main__":
    unittest.main()
