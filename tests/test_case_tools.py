import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class CaseToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "sample.bin"
        self.target.write_bytes(b"local test fixture\x00\xff")
        self.case = self.root / "demoanalysis"

    def run_tool(self, script, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def init(self, *args, expected=0):
        return self.run_tool("new_re_case.py", "--case", "demo", "--root", self.root,
                             "--target", self.target, "--goal", "print expected result",
                             *args, expected=expected)

    def record(self, *args, expected=0):
        return self.run_tool("case_evidence.py", "record", self.case,
                             "--id", "E-001", "--path", "logs/run-001.txt",
                             "--run-id", "run-001", "--command", "manual fixture capture",
                             "--note", "test evidence only", *args, expected=expected)

    def fixture(self):
        self.init()
        (self.case / "logs/run-001.txt").write_text("observed output\n", encoding="utf-8")
        self.record()

    def check(self, expected=0):
        result = self.run_tool("case_evidence.py", "check", self.case,
                               "--strict", "--format", "json", expected=expected)
        return json.loads(result.stdout)

    def test_initialization_records_identity_without_absolute_path(self):
        self.init()
        data = json.loads((self.case / "case.json").read_text(encoding="utf-8"))
        self.assertEqual(data["target"]["path"], "sample.bin")
        self.assertEqual(data["target"]["size"], self.target.stat().st_size)
        self.assertEqual(data["target"]["sha256"], hashlib.sha256(self.target.read_bytes()).hexdigest().upper())
        self.assertEqual(data["status"], "in_progress")
        self.assertTrue((self.case / "STATE.md").is_file())

    def test_dry_run_creates_nothing(self):
        self.init("--dry-run")
        self.assertFalse(self.case.exists())

    def test_missing_target_creates_nothing(self):
        self.target.unlink()
        self.init(expected=2)
        self.assertFalse(self.case.exists())

    def test_directory_target_creates_nothing(self):
        self.init("--target", self.root, expected=2)
        self.assertFalse(self.case.exists())

    def test_existing_case_requires_force(self):
        self.init()
        self.init(expected=2)

    def test_force_preserves_existing_work_and_fills_missing_file(self):
        self.fixture()
        report = self.case / "WRITEUP_demo.md"
        report.write_text("user analysis", encoding="utf-8")
        index = (self.case / "evidence.json").read_bytes()
        metadata = (self.case / "case.json").read_bytes()
        (self.case / "STATE.md").unlink()
        self.init("--force")
        self.assertEqual(report.read_text(encoding="utf-8"), "user analysis")
        self.assertEqual((self.case / "evidence.json").read_bytes(), index)
        self.assertEqual((self.case / "case.json").read_bytes(), metadata)
        self.assertTrue((self.case / "STATE.md").exists())

    def test_force_rejects_changed_target(self):
        self.init()
        original = (self.case / "case.json").read_bytes()
        self.target.write_bytes(b"new version")
        self.init("--force", expected=2)
        self.assertEqual((self.case / "case.json").read_bytes(), original)

    def test_resume_missing_readme_inherits_existing_target_and_goal(self):
        self.init()
        (self.case / "README.md").unlink()
        self.run_tool("new_re_case.py", "--case", "demo", "--root", self.root, "--force")
        text = (self.case / "README.md").read_text(encoding="utf-8")
        self.assertIn("sample.bin", text)
        self.assertIn("print expected result", text)

    def test_absolute_paths_are_opt_in(self):
        self.init("--include-local-paths")
        data = json.loads((self.case / "case.json").read_text(encoding="utf-8"))
        self.assertEqual(data["target"]["path"], str(self.target.resolve()))

    def test_strict_check_is_read_only_and_accepts_intact_evidence(self):
        self.fixture()
        before = {p: p.read_bytes() for p in self.case.rglob("*") if p.is_file()}
        self.assertTrue(self.check()["ok"])
        self.assertEqual(before, {p: p.read_bytes() for p in self.case.rglob("*") if p.is_file()})

    def test_changed_evidence_fails_hash_check(self):
        self.fixture()
        (self.case / "logs/run-001.txt").write_text("changed", encoding="utf-8")
        self.assertIn("SHA256 mismatch", " ".join(self.check(expected=1)["errors"]))

    def test_missing_evidence_fails(self):
        self.fixture()
        (self.case / "logs/run-001.txt").unlink()
        self.check(expected=1)

    def test_duplicate_evidence_id_does_not_overwrite(self):
        self.fixture()
        before = (self.case / "evidence.json").read_bytes()
        self.record(expected=1)
        self.assertEqual((self.case / "evidence.json").read_bytes(), before)

    def test_record_rejects_path_escape_and_mutable_metadata(self):
        self.init()
        for path in ("../sample.bin", str(self.target), "C:/sample.bin", "logs\\x.txt", "case.json", "evidence.json"):
            with self.subTest(path=path):
                self.record("--path", path, expected=1)
        self.assertEqual(json.loads((self.case / "evidence.json").read_text())["records"], [])

    def test_malformed_json_returns_structured_failure(self):
        self.init()
        (self.case / "evidence.json").write_text("{broken", encoding="utf-8")
        self.assertFalse(self.check(expected=1)["ok"])

    def test_malformed_records_return_structured_failure(self):
        self.init()
        for records in ([None], [{"id": "E-001"}], "not a list"):
            (self.case / "evidence.json").write_text(json.dumps({"schema_version": 1, "records": records}), encoding="utf-8")
            self.assertFalse(self.check(expected=1)["ok"])

    def test_empty_case_warns_but_strict_fails(self):
        self.init()
        self.run_tool("case_evidence.py", "check", self.case)
        self.assertFalse(self.check(expected=1)["ok"])

    def test_verified_without_evidence_fails_even_without_strict(self):
        self.init()
        path = self.case / "case.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "verified"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.run_tool("case_evidence.py", "check", self.case, expected=1)

    def test_external_target_is_recorded_by_name(self):
        workspace = self.root / "nested"
        self.init("--root", workspace)
        data = json.loads((workspace / "demoanalysis/case.json").read_text(encoding="utf-8"))
        self.assertEqual(data["target"]["path"], "sample.bin")

    def test_symlink_escape_is_rejected(self):
        self.init()
        link = self.case / "logs/outside.txt"
        try:
            link.symlink_to(self.target)
        except OSError:
            self.skipTest("symlink creation unavailable on this host")
        self.record("--path", "logs/outside.txt", expected=1)

    def test_force_rejects_linked_scaffold_before_writes(self):
        self.init()
        state = self.case / "STATE.md"
        state.unlink()
        try:
            state.symlink_to(self.target)
        except OSError:
            self.skipTest("symlink creation unavailable on this host")
        before = self.target.read_bytes()
        self.init("--force", expected=2)
        self.assertEqual(self.target.read_bytes(), before)

    def test_command_is_saved_as_data_not_executed(self):
        self.init()
        (self.case / "logs/run-001.txt").write_text("fixture", encoding="utf-8")
        marker = self.root / "should-not-exist"
        command = 'python -c "open(%r,\'w\').write(\'bad\')"' % str(marker)
        self.record("--command", command)
        self.assertFalse(marker.exists())
        data = json.loads((self.case / "evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(data["records"][0]["command"], command)


if __name__ == "__main__":
    unittest.main()
