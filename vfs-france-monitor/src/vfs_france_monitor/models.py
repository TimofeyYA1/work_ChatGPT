from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TargetRequest:
    label: str
    url: str
    payload: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def key(self) -> str:
        raw = json.dumps(self.payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TargetRequest":
        return cls(
            label=str(value["label"]),
            url=str(value["url"]),
            payload=dict(value["payload"]),
            headers={str(k): str(v) for k, v in dict(value.get("headers", {})).items()},
        )


@dataclass(frozen=True)
class SlotResult:
    status: str
    available: bool
    earliest_date: str | None
    http_status: int
    raw: dict[str, Any] | str

    @property
    def fingerprint(self) -> str:
        raw = json.dumps(
            {
                "status": self.status,
                "available": self.available,
                "earliest_date": self.earliest_date,
            },
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
