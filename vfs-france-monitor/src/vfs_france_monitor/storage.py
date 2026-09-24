from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import TargetRequest


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_targets(path: Path) -> list[TargetRequest]:
    return [TargetRequest.from_dict(item) for item in _load_json(path, [])]


def save_targets(path: Path, targets: list[TargetRequest]) -> None:
    _save_json(path, [target.to_dict() for target in targets])


def load_monitor_state(path: Path) -> dict[str, Any]:
    return dict(_load_json(path, {"targets": {}}))


def save_monitor_state(path: Path, state: dict[str, Any]) -> None:
    _save_json(path, state)
