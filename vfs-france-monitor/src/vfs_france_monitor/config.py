from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    telegram_bot_token: str
    telegram_chat_id: str
    check_interval_seconds: float
    check_jitter_seconds: float
    per_target_delay_seconds: float
    heartbeat_hours: float
    headless: bool
    vfs_login_url: str
    vfs_dashboard_url: str
    vfs_booking_url: str
    vfs_slot_url: str

    @property
    def storage_state_path(self) -> Path:
        return self.data_dir / "storage_state.json"

    @property
    def targets_path(self) -> Path:
        return self.data_dir / "targets.json"

    @property
    def monitor_state_path(self) -> Path:
        return self.data_dir / "monitor_state.json"


def load_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR", "./data")).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        data_dir=data_dir,
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        check_interval_seconds=float(os.getenv("CHECK_INTERVAL_SECONDS", "75")),
        check_jitter_seconds=float(os.getenv("CHECK_JITTER_SECONDS", "15")),
        per_target_delay_seconds=float(os.getenv("PER_TARGET_DELAY_SECONDS", "2.5")),
        heartbeat_hours=float(os.getenv("HEARTBEAT_HOURS", "6")),
        headless=_bool_env("HEADLESS", True),
        vfs_login_url=os.getenv(
            "VFS_LOGIN_URL", "https://visa.vfsglobal.com/rus/en/fra/login"
        ),
        vfs_dashboard_url=os.getenv(
            "VFS_DASHBOARD_URL", "https://visa.vfsglobal.com/rus/en/fra/dashboard"
        ),
        vfs_booking_url=os.getenv(
            "VFS_BOOKING_URL",
            "https://visa.vfsglobal.com/rus/en/fra/book-appointment/application-detail",
        ),
        vfs_slot_url=os.getenv(
            "VFS_SLOT_URL",
            "https://lift-api.vfsglobal.com/appointment/CheckIsSlotAvailable",
        ),
    )
