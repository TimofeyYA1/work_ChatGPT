from __future__ import annotations

import asyncio
import random
import time
from datetime import datetime, timezone

from .config import Settings
from .notifier import TelegramNotifier
from .storage import load_monitor_state, load_targets, save_monitor_state
from .vfs import SessionExpired, VfsClient


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


async def run_monitor(settings: Settings) -> None:
    targets = load_targets(settings.targets_path)
    if not targets:
        raise RuntimeError(f"No targets in {settings.targets_path}. Run vfs-france-bootstrap first.")

    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    state = load_monitor_state(settings.monitor_state_path)
    state.setdefault("targets", {})
    last_heartbeat = float(state.get("last_heartbeat_epoch", 0))
    session_alerted = False
    warmup_counter = 0

    await notifier.send(
        f"VFS France monitor started. Targets: {', '.join(t.label for t in targets)}"
    )

    while True:
        try:
            async with VfsClient(settings) as client:
                await client.warm_up()
                session_alerted = False

                while True:
                    warmup_counter += 1
                    if warmup_counter % 20 == 0:
                        await client.warm_up()

                    for target in targets:
                        result = await client.check(target)
                        target_state = state["targets"].setdefault(target.key, {})
                        previous_status = target_state.get("status")
                        previous_fingerprint = target_state.get("fingerprint")

                        target_state.update(
                            {
                                "label": target.label,
                                "status": result.status,
                                "fingerprint": result.fingerprint,
                                "last_checked_at": _utc_now(),
                                "http_status": result.http_status,
                            }
                        )

                        if result.available and (
                            previous_status != "available" or previous_fingerprint != result.fingerprint
                        ):
                            date_text = result.earliest_date or "date not returned"
                            await notifier.send(
                                "🚨 VFS FRANCE SLOT FOUND\n"
                                f"Target: {target.label}\n"
                                f"Earliest date: {date_text}\n"
                                f"Checked: {_utc_now()}\n"
                                "Open VFS and book immediately."
                            )

                        save_monitor_state(settings.monitor_state_path, state)
                        await asyncio.sleep(settings.per_target_delay_seconds)

                    now = time.time()
                    if now - last_heartbeat >= settings.heartbeat_hours * 3600:
                        closed = sum(
                            1
                            for t in targets
                            if state["targets"].get(t.key, {}).get("status") == "no_slots"
                        )
                        await notifier.send(
                            f"VFS monitor heartbeat: alive, {len(targets)} targets, {closed} currently closed."
                        )
                        last_heartbeat = now
                        state["last_heartbeat_epoch"] = last_heartbeat
                        save_monitor_state(settings.monitor_state_path, state)

                    delay = max(
                        30.0,
                        settings.check_interval_seconds
                        + random.uniform(-settings.check_jitter_seconds, settings.check_jitter_seconds),
                    )
                    await asyncio.sleep(delay)

        except SessionExpired as exc:
            if not session_alerted:
                await notifier.send(
                    "⚠️ VFS session expired. Run vfs-france-bootstrap again to refresh the session. "
                    f"Reason: {exc}"
                )
                session_alerted = True
            await asyncio.sleep(600)
        except Exception as exc:
            await notifier.send(f"⚠️ VFS monitor error: {type(exc).__name__}: {exc}")
            await asyncio.sleep(120)
