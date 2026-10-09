"""Shared local case I/O; standard library only, Python 3.8+."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def local_file(root: Path, name: str) -> Path:
    """Accept only portable paths resolving inside the case."""
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("artifact path must use case-relative forward slashes")
    relative = PurePosixPath(name)
    if relative.is_absolute() or PureWindowsPath(name).drive or ".." in relative.parts:
        raise ValueError("artifact path must remain inside the case")
    path = root / name
    path.resolve().relative_to(root.resolve())
    if not path.is_file():
        raise ValueError("artifact is not a regular file: " + name)
    return path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    """Replace a complete JSON document, refusing linked metadata files."""
    if path.is_symlink():
        raise ValueError("refusing linked metadata file: " + path.name)
    descriptor, temporary = tempfile.mkstemp(prefix=".autore-", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
