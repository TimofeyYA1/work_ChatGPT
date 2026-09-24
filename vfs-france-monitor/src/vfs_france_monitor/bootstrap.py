from __future__ import annotations

import asyncio
import json
from typing import Any

from playwright.async_api import Request, async_playwright

from .config import load_settings
from .models import TargetRequest
from .storage import load_targets, save_targets
from .vfs import HEADER_WHITELIST


async def bootstrap() -> None:
    settings = load_settings()
    captures: list[dict[str, Any]] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        async def capture(request: Request) -> None:
            if settings.vfs_slot_url.lower() not in request.url.lower() or request.method != "POST":
                return
            try:
                payload = request.post_data_json
                headers = await request.all_headers()
            except Exception:
                return
            if not isinstance(payload, dict):
                return
            captures.append(
                {
                    "url": request.url,
                    "payload": payload,
                    "headers": {
                        k.lower(): v
                        for k, v in headers.items()
                        if k.lower() in HEADER_WHITELIST and v
                    },
                }
            )
            print("\nCaptured VFS slot check:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))

        page.on("request", lambda req: asyncio.create_task(capture(req)))
        await page.goto(settings.vfs_login_url, wait_until="domcontentloaded", timeout=60_000)

        print(
            "\n1) Log in to VFS manually in the opened browser.\n"
            "2) Start a new booking and choose the centre/category/subcategory you want to monitor.\n"
            "3) Repeat for every centre you want. Each slot-check request will be captured.\n"
            "4) Return here and press Enter.\n"
        )
        await asyncio.to_thread(input, "Press Enter when finished: ")

        await context.storage_state(path=str(settings.storage_state_path))
        await browser.close()

    unique: dict[str, dict[str, Any]] = {}
    for item in captures:
        key = json.dumps(item["payload"], sort_keys=True, ensure_ascii=False)
        unique[key] = item

    if not unique:
        raise RuntimeError(
            "No CheckIsSlotAvailable request was captured. "
            "Open the booking flow and select a centre/category before finishing bootstrap."
        )

    existing = {target.key: target for target in load_targets(settings.targets_path)}
    for item in unique.values():
        provisional = TargetRequest(
            label="",
            url=item["url"],
            payload=item["payload"],
            headers=item["headers"],
        )
        old = existing.get(provisional.key)
        default_label = old.label if old else _default_label(item["payload"])
        label = (await asyncio.to_thread(input, f"Label [{default_label}]: ")).strip() or default_label
        provisional.label = label
        existing[provisional.key] = provisional

    save_targets(settings.targets_path, list(existing.values()))
    print(f"Saved session: {settings.storage_state_path}")
    print(f"Saved {len(existing)} target(s): {settings.targets_path}")


def _default_label(payload: dict[str, Any]) -> str:
    vac = payload.get("vacCode") or payload.get("centerCode") or "centre"
    cat = payload.get("visaCategoryCode") or "category"
    return f"{vac} / {cat}"


def cli() -> None:
    asyncio.run(bootstrap())


if __name__ == "__main__":
    cli()
