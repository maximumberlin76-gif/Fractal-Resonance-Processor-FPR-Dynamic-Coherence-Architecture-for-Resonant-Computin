#!/usr/bin/env python3
"""Data-only artifact validation primitives for FRP M25.

This module deliberately has no command runner, dynamic importer, serializer,
template engine, or executable-object loader.  It accepts bounded UTF-8 JSON
objects, exact SHA-256 digests, regular files, and repository-relative paths.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


MAX_ARTIFACT_BYTES = 1_048_576


class FailureCode:
    """Stable machine-readable M25 failure classifications."""

    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    MALFORMED_JSON = "MALFORMED_JSON"
    DUPLICATE_JSON_KEY = "DUPLICATE_JSON_KEY"
    INCOMPLETE_PACKAGE = "INCOMPLETE_PACKAGE"
    UNEXPECTED_ARTIFACT = "UNEXPECTED_ARTIFACT"
    INVALID_DOCUMENT = "INVALID_DOCUMENT"
    UNSAFE_PATH = "UNSAFE_PATH"
    OVERSIZED_ARTIFACT = "OVERSIZED_ARTIFACT"
    NON_REGULAR_FILE = "NON_REGULAR_FILE"


class ValidationFailure(ValueError):
    """A classified validation failure with inert text-only detail."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def safe_relative_path(value: str) -> PurePosixPath:
    """Return a strict repository-relative POSIX path or reject it."""

    if not isinstance(value, str):
        raise ValidationFailure(FailureCode.UNSAFE_PATH, "path is not text")
    path = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or path.is_absolute()
        or any(part in ("", ".", "..") for part in value.split("/"))
    ):
        raise ValidationFailure(FailureCode.UNSAFE_PATH, value)
    return path


def sha256_bytes(raw: bytes) -> str:
    """Return the lowercase SHA-256 digest of inert bytes."""

    if not isinstance(raw, bytes):
        raise ValidationFailure(FailureCode.INVALID_DOCUMENT, "payload is not bytes")
    return hashlib.sha256(raw).hexdigest()


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationFailure(FailureCode.DUPLICATE_JSON_KEY, key)
        result[key] = value
    return result


def decode_json_object(raw: bytes, label: str) -> dict[str, Any]:
    """Decode one bounded JSON object without hooks capable of execution."""

    if not isinstance(raw, bytes):
        raise ValidationFailure(FailureCode.INVALID_DOCUMENT, f"{label}: not bytes")
    if len(raw) > MAX_ARTIFACT_BYTES:
        raise ValidationFailure(
            FailureCode.OVERSIZED_ARTIFACT,
            f"{label}: {len(raw)} > {MAX_ARTIFACT_BYTES}",
        )
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except ValidationFailure:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValidationFailure(FailureCode.MALFORMED_JSON, f"{label}: {exc}") from None
    if not isinstance(value, dict):
        raise ValidationFailure(FailureCode.INVALID_DOCUMENT, f"{label}: root is not object")
    return value


def validate_package_bytes(
    package: Mapping[str, bytes],
    required_paths: Sequence[str],
    expected_digests: Mapping[str, str],
) -> dict[str, Any]:
    """Validate an exact closed JSON package held entirely as inert bytes."""

    if not isinstance(package, Mapping):
        raise ValidationFailure(FailureCode.INVALID_DOCUMENT, "package is not a mapping")
    required = tuple(required_paths)
    if len(required) != len(set(required)):
        raise ValidationFailure(FailureCode.INVALID_DOCUMENT, "duplicate required path")
    for relative in required:
        safe_relative_path(relative)
    present = set(package)
    required_set = set(required)
    missing = sorted(required_set - present)
    if missing:
        raise ValidationFailure(FailureCode.INCOMPLETE_PACKAGE, ",".join(missing))
    unexpected = sorted(present - required_set)
    if unexpected:
        raise ValidationFailure(FailureCode.UNEXPECTED_ARTIFACT, ",".join(unexpected))
    if set(expected_digests) != required_set:
        raise ValidationFailure(FailureCode.INCOMPLETE_PACKAGE, "digest map is not closed")

    documents: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    for relative in required:
        safe_relative_path(relative)
        raw = package[relative]
        if not isinstance(raw, bytes):
            raise ValidationFailure(FailureCode.INVALID_DOCUMENT, f"{relative}: not bytes")
        observed = sha256_bytes(raw)
        expected = expected_digests[relative]
        if observed != expected:
            raise ValidationFailure(
                FailureCode.DIGEST_MISMATCH,
                f"{relative}: expected {expected}, observed {observed}",
            )
        documents[relative] = decode_json_object(raw, relative)
        records.append({"path": relative, "bytes": len(raw), "raw_sha256": observed})
    return {
        "status": "PASS",
        "artifact_count": len(records),
        "records": records,
        "documents": documents,
    }


def load_package_from_root(root: Path, required_paths: Sequence[str]) -> dict[str, bytes]:
    """Read only named, bounded, non-symlink regular files below root."""

    root = root.resolve()
    if root.is_symlink() or not root.is_dir():
        raise ValidationFailure(FailureCode.NON_REGULAR_FILE, "invalid repository root")
    package: dict[str, bytes] = {}
    for relative in required_paths:
        path = safe_relative_path(relative)
        target = root.joinpath(*path.parts)
        if target.is_symlink() or not target.is_file():
            raise ValidationFailure(FailureCode.NON_REGULAR_FILE, relative)
        raw = target.read_bytes()
        if len(raw) > MAX_ARTIFACT_BYTES:
            raise ValidationFailure(FailureCode.OVERSIZED_ARTIFACT, relative)
        package[relative] = raw
    return package
