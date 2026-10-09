#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from case_utils import read_json, sha256_file, write_json


def safe_display_path(target: Path, root: Path, include_local_paths: bool) -> str:
    if include_local_paths:
        return str(target)
    try:
        return target.relative_to(root).as_posix()
    except ValueError:
        return target.name


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or resume a local RE case (Python 3.8+).")
    parser.add_argument("--case", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--target", type=Path, help="Existing file to identify; never executed or copied")
    parser.add_argument("--goal", default="", help="Observable success condition")
    parser.add_argument("--force", action="store_true", help="Fill missing scaffold files; never overwrite work")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs without writing")
    parser.add_argument("--include-local-paths", action="store_true", help="Opt into absolute target paths")
    args = parser.parse_args()
    try:
        case = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in args.case.strip())
        if not case:
            raise ValueError("--case produced an empty safe name")
        root = args.root.resolve()
        out = root / (case + "analysis")
        if out.is_symlink():
            raise ValueError("analysis directory must not be a symlink")
        out.resolve().relative_to(root)
        if out.exists() and (not out.is_dir() or not args.force):
            raise ValueError("analysis directory already exists; use --force to fill missing files")
        target = None
        if args.target is not None:
            source = args.target.resolve()
            if not source.is_file():
                raise ValueError("--target must be an existing regular file")
            target = {"path": safe_display_path(source, root, args.include_local_paths),
                      "size": source.stat().st_size, "sha256": sha256_file(source)}
        directories = ("code", "logs", "screenshots", "dumps", "runs")
        names = ("case.json", "evidence.json", "README.md", "STATE.md", "WRITEUP_" + case + ".md")
        for name in directories + names:
            path = out / name
            if path.is_symlink():
                raise ValueError("refusing linked scaffold path: " + name)
            path.resolve().relative_to(out.resolve())
            if path.exists() and (path.is_dir() != (name in directories)):
                raise ValueError("unexpected scaffold path type: " + name)
        if (out / "case.json").exists():
            old = read_json(out / "case.json")
            if not isinstance(old, dict) or old.get("schema_version") != 1 or old.get("case") != case:
                raise ValueError("existing case metadata is incompatible")
            if target is not None and old.get("target") != target:
                raise ValueError("target identity differs; use a new case directory")
            if args.goal and old.get("goal") != args.goal:
                raise ValueError("goal differs; update existing case metadata explicitly")
            # Missing documents on resume inherit the established identity/goal.
            target = old.get("target")
            if target is not None and (not isinstance(target, dict) or
                                      not all(key in target for key in ("path", "size", "sha256"))):
                raise ValueError("existing target identity is invalid")
            args.goal = old.get("goal", "")
            if not isinstance(args.goal, str):
                raise ValueError("existing goal must be a string")
        if args.dry_run:
            print("Would initialize: " + str(out))
            return 0
        for name in directories:
            (out / name).mkdir(parents=True, exist_ok=True)
        metadata = {"schema_version": 1, "case": case,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "goal": args.goal, "status": "in_progress", "target": target}
        if not (out / "case.json").exists():
            write_json(out / "case.json", metadata)
        if not (out / "evidence.json").exists():
            write_json(out / "evidence.json", {"schema_version": 1, "records": []})
        identity = ("- Path: `{path}`\n- Size: `{size}`\n- SHA256: `{sha256}`".format(**target)
                    if target else "- Target identity: not recorded")
        documents = {
            "README.md": "# " + case + " Analysis\n\n## Target\n\n" + identity +
                "\n\n## Goal\n\n" + (args.goal or "Define the observable success condition.") +
                "\n\n## Layout\n\n- `case.json`: target identity, goal, status\n"
                "- `STATE.md`: decisions and next action for resuming\n"
                "- `evidence.json`: indexed artifacts and SHA256\n"
                "- `code/`: scripts; `logs/`: raw logs; `screenshots/`: proof images\n"
                "- `dumps/`: runtime images; `runs/`: environment and rollback notes\n",
            "STATE.md": "# Resume State\n\n- Phase: triage\n- Controller: unassigned\n"
                "- Latest run ID: none\n- Verified facts (Evidence IDs): none\n"
                "- Hypotheses / failed attempts: none\n- Modified files / processes: none\n"
                "- Rollback procedure: not needed yet\n- Blocker: none\n"
                "- Next action: identify target and record baseline\n",
            "WRITEUP_" + case + ".md": "# " + case + " Writeup\n\n## Target\n\n" + identity +
                "\n\n## Goal\n\n" + (args.goal or "Define success and reject false positives.") +
                "\n\n## Findings\n\n| Finding | Evidence IDs | Confidence / limitations |\n"
                "| --- | --- | --- |\n\n## Method\n\nNot recorded.\n\n"
                "## Verification\n\nNot run.\n\n## Reproduction\n\nNot recorded.\n\n"
                "## Rollback\n\nNot recorded.\n"}
        for name, content in documents.items():
            if not (out / name).exists():
                with (out / name).open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(content)
        print(out)
        return 0
    except (OSError, ValueError) as exc:
        parser.exit(2, "error: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
