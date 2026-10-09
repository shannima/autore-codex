#!/usr/bin/env python3
"""Record local evidence or check its integrity; does not execute a target."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from case_utils import local_file, read_json, sha256_file, write_json


def load_index(root):
    data = read_json(local_file(root, "evidence.json"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("records"), list):
        raise ValueError("invalid evidence.json schema")
    seen = set()
    for item in data["records"]:
        if not isinstance(item, dict):
            raise ValueError("evidence record must be an object")
        for key in ("id", "path", "sha256", "run_id", "command", "note", "created_at"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError("missing or empty evidence field: " + key)
        if not re.fullmatch(r"E-[0-9]{3,}", item["id"]) or item["id"] in seen:
            raise ValueError("invalid or duplicate evidence ID: " + item["id"])
        if not re.fullmatch(r"[0-9a-fA-F]{64}", item["sha256"]):
            raise ValueError("invalid SHA256 for " + item["id"])
        seen.add(item["id"])
    return data


def check(root):
    errors, warnings = [], []
    case = read_json(local_file(root, "case.json"))
    if not isinstance(case, dict) or case.get("schema_version") != 1:
        raise ValueError("invalid case.json schema")
    if not isinstance(case.get("case"), str) or not case["case"].strip():
        errors.append("case name is missing")
    if case.get("status") not in ("in_progress", "blocked", "verified", "failed"):
        errors.append("invalid case status")
    if not isinstance(case.get("goal"), str) or not case["goal"].strip():
        warnings.append("observable goal is missing")
    target = case.get("target")
    if target is None:
        warnings.append("target identity is missing")
    elif (not isinstance(target, dict) or not isinstance(target.get("path"), str)
          or not target["path"].strip() or type(target.get("size")) is not int or target["size"] < 0
          or not isinstance(target.get("sha256"), str)
          or not re.fullmatch(r"[0-9a-fA-F]{64}", target["sha256"])):
        errors.append("invalid target identity")
    index = load_index(root)
    for item in index["records"]:
        try:
            path = local_file(root, item["path"])
            if path.resolve() in ((root / "evidence.json").resolve(), (root / "case.json").resolve()):
                raise ValueError("mutable case metadata cannot be evidence")
            if sha256_file(path) != item["sha256"].upper():
                errors.append(item["id"] + ": SHA256 mismatch")
        except (OSError, ValueError) as exc:
            errors.append(item["id"] + ": " + str(exc))
    if not index["records"]:
        warnings.append("no evidence records")
    if case.get("status") == "verified" and warnings:
        errors.append("verified status requires a goal, target identity and evidence")
    return {"ok": not errors, "records": len(index["records"]),
            "errors": errors, "warnings": warnings,
            "scope": "Artifact integrity only; goal satisfaction requires human review."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    record = sub.add_parser("record", help="Append evidence; single writer required")
    record.add_argument("case_root", type=Path)
    for name in ("id", "path", "run-id", "command", "note"):
        record.add_argument("--" + name, required=True)
    verify = sub.add_parser("check", help="Read-only metadata and hash check")
    verify.add_argument("case_root", type=Path)
    verify.add_argument("--strict", action="store_true", help="Treat incomplete metadata warnings as failures")
    verify.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    try:
        root = args.case_root.resolve()
        if args.action == "record":
            # Check the case identity is readable before editing its index.
            case = read_json(local_file(root, "case.json"))
            if not isinstance(case, dict) or case.get("schema_version") != 1:
                raise ValueError("invalid case.json schema")
            index = load_index(root)
            if not re.fullmatch(r"E-[0-9]{3,}", args.id):
                raise ValueError("--id must be E- followed by at least three digits")
            if any(item["id"] == args.id for item in index["records"]):
                raise ValueError("evidence ID already exists")
            if not all(value.strip() for value in (args.run_id, args.command, args.note)):
                raise ValueError("run ID, command and note must not be empty")
            path = local_file(root, args.path)
            if path.resolve() in ((root / "evidence.json").resolve(), (root / "case.json").resolve()):
                raise ValueError("mutable case metadata cannot be evidence")
            index["records"].append({"id": args.id, "path": args.path,
                "sha256": sha256_file(path), "run_id": args.run_id,
                "command": args.command, "note": args.note,
                "created_at": datetime.now(timezone.utc).isoformat()})
            write_json(root / "evidence.json", index)
            print("Recorded " + args.id)
            return 0
        result = check(root)
        if args.strict and result["warnings"]:
            result["ok"] = False
    except (OSError, ValueError) as exc:
        result = {"ok": False, "records": 0, "errors": [str(exc)], "warnings": []}
    if getattr(args, "format", "text") == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result["ok"] else "FAIL")
        for kind in ("errors", "warnings"):
            for message in result[kind]:
                print(kind + ": " + message)
        if "scope" in result:
            print(result["scope"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
