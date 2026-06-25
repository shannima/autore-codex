#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def safe_display_path(target: Path, root: Path, include_local_paths: bool) -> str:
    if include_local_paths:
        return str(target)
    try:
        return target.relative_to(root).as_posix()
    except ValueError:
        return target.name


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a reusable RE case analysis folder.")
    parser.add_argument("--case", required=True, help="Case name, for example zidan or 0618")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root directory where <case>analysis will be created")
    parser.add_argument("--target", type=Path, help="Optional target binary to hash and record")
    parser.add_argument("--force", action="store_true", help="Allow using an existing analysis directory")
    parser.add_argument(
        "--include-local-paths",
        action="store_true",
        help="Write absolute local paths into Markdown. Off by default for upload safety.",
    )
    args = parser.parse_args()

    case = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in args.case.strip())
    if not case:
        raise SystemExit("--case produced an empty safe name")

    root = args.root.resolve()
    out = root / f"{case}analysis"
    if out.exists() and not args.force:
        raise SystemExit(f"Analysis directory already exists: {out} (use --force to reuse it)")

    for child in ["code", "logs", "screenshots", "dumps"]:
        (out / child).mkdir(parents=True, exist_ok=True)

    target_lines = []
    if args.target:
        target = args.target.resolve()
        target_lines.append(f"- Path: `{safe_display_path(target, root, args.include_local_paths)}`")
        if target.exists():
            target_lines.append(f"- Size: `{target.stat().st_size}`")
            target_lines.append(f"- SHA256: `{sha256_file(target)}`")
        else:
            target_lines.append("- Size: target not found")
            target_lines.append("- SHA256: target not found")

    readme = out / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {case} Analysis\n\n"
            "## Target\n\n"
            + ("\n".join(target_lines) if target_lines else "- Path:\n- Size:\n- SHA256:")
            + "\n\n## Goal\n\n"
            "- Define the exact success condition here.\n\n"
            "## Layout\n\n"
            "- `code/`: scripts and probes\n"
            "- `logs/`: raw run logs\n"
            "- `screenshots/`: proof images\n"
            "- `dumps/`: runtime dumps\n",
            encoding="utf-8",
        )

    writeup = out / f"WRITEUP_{case}.md"
    if not writeup.exists():
        writeup.write_text(
            f"# {case} Writeup\n\n"
            "## Target\n\n"
            + ("\n".join(target_lines) if target_lines else "- Path:\n- Size:\n- SHA256:")
            + "\n\n## Goal\n\n"
            "Describe the exact success condition and false positives.\n\n"
            "## Method\n\n"
            "TBD\n\n"
            "## Verification\n\n"
            "TBD\n\n"
            "## Reproduction\n\n"
            "TBD\n",
            encoding="utf-8",
        )

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
