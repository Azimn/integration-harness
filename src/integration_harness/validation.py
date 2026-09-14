from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

HEX40 = re.compile(r"^[0-9a-f]{40}$")
VALID_DECISIONS = {
    "concept_only",
    "test_pattern",
    "wrap",
    "adapt",
    "direct_reuse",
    "reject",
}
VALID_DONOR_STATUS = {"discovery", "provisional", "accepted", "rejected"}
VALID_REVIEW_VERDICTS = {"pass", "revise", "fail"}
VALID_SEVERITIES = {"low", "medium", "high"}
VALID_OBJECTION_STATUS = {"open", "resolved", "rejected"}


class ValidationError(ValueError):
    pass


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def _require_text(obj: dict[str, Any], key: str, where: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{where}.{key} must be non-empty text")
    return value.strip()


def _require_string_list(obj: dict[str, Any], key: str, where: str) -> list[str]:
    value = obj.get(key)
    if not isinstance(value, list) or not value:
        raise ValidationError(f"{where}.{key} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValidationError(f"{where}.{key} must contain only non-empty strings")
    return [item.strip() for item in value]


def validate_registry(path: str | Path) -> list[str]:
    path = Path(path)
    data = _load_json(path)
    if not isinstance(data, dict):
        raise ValidationError("registry root must be an object")
    if data.get("schema_version") != 2:
        raise ValidationError("registry schema_version must be 2")
    donors = data.get("donors")
    if not isinstance(donors, list) or not donors:
        raise ValidationError("registry donors must be a non-empty list")

    seen_donors: set[str] = set()
    validated: list[str] = []
    for index, donor in enumerate(donors):
        where = f"donors[{index}]"
        if not isinstance(donor, dict):
            raise ValidationError(f"{where} must be an object")

        donor_id = _require_text(donor, "id", where)
        if donor_id in seen_donors:
            raise ValidationError(f"duplicate donor id: {donor_id}")
        seen_donors.add(donor_id)

        repository = _require_text(donor, "repository", where)
        if repository.count("/") != 1:
            raise ValidationError(f"{where}.repository must use owner/name form")

        revision = _require_text(donor, "revision", where)
        if not HEX40.fullmatch(revision):
            raise ValidationError(f"{where}.revision must be a 40-character git SHA")

        license_name = _require_text(donor, "license", where)
        status = _require_text(donor, "status", where)
        _require_text(donor, "notes", where)
        if status not in VALID_DONOR_STATUS:
            raise ValidationError(f"{where}.status has unsupported value {status!r}")
        if status == "accepted" and license_name.lower() == "verify":
            raise ValidationError(f"{where} cannot be accepted before license verification")

        components = donor.get("components")
        if not isinstance(components, list) or not components:
            raise ValidationError(f"{where}.components must be a non-empty list")

        seen_components: set[str] = set()
        for component_index, component in enumerate(components):
            cwhere = f"{where}.components[{component_index}]"
            if not isinstance(component, dict):
                raise ValidationError(f"{cwhere} must be an object")
            component_id = _require_text(component, "id", cwhere)
            if component_id in seen_components:
                raise ValidationError(f"duplicate component id in {donor_id}: {component_id}")
            seen_components.add(component_id)

            decision = _require_text(component, "decision", cwhere)
            _require_text(component, "claim", cwhere)
            _require_string_list(component, "evidence", cwhere)
            _require_text(component, "notes", cwhere)
            if decision not in VALID_DECISIONS:
                raise ValidationError(f"{cwhere}.decision has unsupported value {decision!r}")
            if decision == "direct_reuse" and license_name.lower() == "verify":
                raise ValidationError(
                    f"{cwhere} cannot directly reuse code before license verification"
                )

        validated.append(donor_id)
    return validated


def _validate_review_data(path: Path) -> dict[str, Any]:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise ValidationError(f"review root must be an object: {path}")
    if data.get("schema_version") != 1:
        raise ValidationError(f"review schema_version must be 1: {path}")

    _require_text(data, "experiment_id", str(path))
    revision = _require_text(data, "implementation_revision", str(path))
    if not HEX40.fullmatch(revision):
        raise ValidationError(f"{path}.implementation_revision must be a 40-character git SHA")
    _require_text(data, "reviewer_role", str(path))
    verdict = _require_text(data, "verdict", str(path))
    if verdict not in VALID_REVIEW_VERDICTS:
        raise ValidationError(f"{path}.verdict has unsupported value {verdict!r}")

    objections = data.get("objections")
    if not isinstance(objections, list):
        raise ValidationError(f"{path}.objections must be a list")

    open_high = 0
    for index, objection in enumerate(objections):
        where = f"{path}.objections[{index}]"
        if not isinstance(objection, dict):
            raise ValidationError(f"{where} must be an object")
        _require_text(objection, "id", where)
        severity = _require_text(objection, "severity", where)
        status = _require_text(objection, "status", where)
        _require_text(objection, "claim", where)
        _require_text(objection, "evidence", where)
        _require_text(objection, "disposition", where)
        if severity not in VALID_SEVERITIES:
            raise ValidationError(f"{where}.severity has unsupported value {severity!r}")
        if status not in VALID_OBJECTION_STATUS:
            raise ValidationError(f"{where}.status has unsupported value {status!r}")
        if severity == "high" and status == "open":
            open_high += 1

    if verdict == "pass" and open_high:
        raise ValidationError(f"{path} cannot pass with {open_high} open high-severity objection(s)")
    return data


def validate_review(path: str | Path) -> str:
    path = Path(path)
    data = _validate_review_data(path)
    return str(data["experiment_id"])


def validate_reviews(directory: str | Path) -> list[str]:
    directory = Path(directory)
    if not directory.exists():
        return []
    validated: list[str] = []
    for path in sorted(directory.glob("*.json")):
        validated.append(validate_review(path))
    return validated


def _git_is_ancestor(revision: str, head_revision: str, repo_root: Path) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", revision, head_revision],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise ValidationError(
        "git could not evaluate review ancestry: " + result.stderr.strip()
    )


def _git_changed_paths(revision: str, head_revision: str, repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{revision}..{head_revision}"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValidationError(
            "git could not inspect post-review changes: " + result.stderr.strip()
        )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _post_review_paths_allowed(paths: list[str]) -> bool:
    return all(
        path.startswith("reviews/") and path.endswith(".json") and "/" not in path[8:]
        for path in paths
    )


def validate_review_gate(
    directory: str | Path,
    head_revision: str,
    repo_root: str | Path = ".",
    *,
    is_ancestor: Callable[[str, str, Path], bool] | None = None,
    changed_paths: Callable[[str, str, Path], list[str]] | None = None,
) -> str:
    """Require a passing review of the latest substantive repository state.

    A review records the implementation commit it examined. The review artifact
    itself necessarily lands in a later commit, so exact HEAD equality would be
    self-referential. The gate therefore accepts a passing review only when its
    implementation revision is an ancestor of HEAD and every later tree change
    is another machine-readable review artifact directly under ``reviews/``.
    """
    directory = Path(directory)
    repo_root = Path(repo_root)
    if not directory.exists():
        raise ValidationError("review gate requires a reviews directory")

    ancestor_fn = is_ancestor or _git_is_ancestor
    changed_fn = changed_paths or _git_changed_paths
    candidates: list[tuple[int, str]] = []

    for path in sorted(directory.glob("*.json")):
        data = _validate_review_data(path)
        if data["verdict"] != "pass":
            continue
        revision = str(data["implementation_revision"])
        if not ancestor_fn(revision, head_revision, repo_root):
            continue
        paths = changed_fn(revision, head_revision, repo_root)
        if not _post_review_paths_allowed(paths):
            continue
        candidates.append((len(paths), str(data["experiment_id"])))

    if not candidates:
        raise ValidationError(
            "no passing review covers the current substantive state; add a review "
            "for the latest implementation commit and make no non-review changes afterward"
        )

    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]
