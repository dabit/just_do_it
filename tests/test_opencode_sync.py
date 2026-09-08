"""Characterizes OpenCode sync behavior while Codex gets an independent package."""

import os
import pathlib
import subprocess
import tempfile
import unittest

import jdi_files


def expected_commands():
    return {
        "jdi-%s" % pathlib.PurePosixPath(path).name
        for path in jdi_files.markdown_files("commands")
    }


def expected_agents():
    return {
        "jdi-%s" % pathlib.PurePosixPath(path).name
        for path in jdi_files.markdown_files("agents")
    }


def names(directory):
    return {path.name for path in directory.iterdir() if path.is_file()}


def all_text(directory):
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    )


def run_sync(*arguments, env=None):
    return subprocess.run(
        [str(jdi_files.ROOT / "bin" / "sync-opencode.sh"), *arguments],
        cwd=jdi_files.ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


class OpenCodeGlobalSyncTest(unittest.TestCase):
    def test_global_sync_preserves_command_agent_inventory_and_checkout_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = pathlib.Path(temporary)
            env = os.environ.copy()
            env["OPENCODE_CONFIG_DIR"] = str(destination)
            result = run_sync("--global", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(names(destination / "command"), expected_commands())
            self.assertEqual(names(destination / "agent"), expected_agents())
            synced = all_text(destination)
            self.assertIn(str(jdi_files.ROOT), synced)
            self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", synced)
            self.assertFalse((destination / "jdi").exists())


class OpenCodeProjectSyncTest(unittest.TestCase):
    def test_project_sync_copies_dependencies_and_uses_only_portable_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = pathlib.Path(temporary)
            result = run_sync("--project", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)
            destination = project / ".opencode"
            self.assertEqual(names(destination / "command"), expected_commands())
            self.assertEqual(names(destination / "agent"), expected_agents())
            self.assertEqual(
                names(destination / "jdi" / "reference"),
                {
                    pathlib.PurePosixPath(path).name
                    for path in jdi_files.markdown_files("reference")
                },
            )
            self.assertEqual(
                names(destination / "jdi" / "roles"),
                {
                    pathlib.PurePosixPath(path).name
                    for path in jdi_files.markdown_files("roles")
                },
            )
            synced = all_text(destination)
            self.assertIn(".opencode/jdi", synced)
            self.assertNotIn(str(jdi_files.ROOT), synced)
            self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", synced)


class OpenCodeSyncIsolationTest(unittest.TestCase):
    def test_codex_package_is_not_synced_into_opencode(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            global_destination = root / "global"
            global_destination.mkdir()
            env = os.environ.copy()
            env["OPENCODE_CONFIG_DIR"] = str(global_destination)
            global_result = run_sync("--global", env=env)
            self.assertEqual(global_result.returncode, 0, global_result.stderr)

            project = root / "project"
            project.mkdir()
            project_result = run_sync("--project", str(project))
            self.assertEqual(project_result.returncode, 0, project_result.stderr)

            for destination in (global_destination, project / ".opencode"):
                with self.subTest(destination=destination):
                    relative_paths = {
                        path.relative_to(destination).as_posix()
                        for path in destination.rglob("*")
                    }
                    self.assertFalse(
                        any(".codex-plugin" in path for path in relative_paths),
                        relative_paths,
                    )
                    self.assertFalse(
                        any(
                            path == "skills" or path.startswith("skills/")
                            for path in relative_paths
                        ),
                        relative_paths,
                    )


if __name__ == "__main__":
    unittest.main()
