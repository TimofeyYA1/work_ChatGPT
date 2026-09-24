from __future__ import annotations

import asyncio
import json
from typing import Any

from playwright.async_api import Browser, BrowserContext, Page, Request, async_playwright

from .config import Settings
from .models import SlotResult, TargetRequest

HEADER_WHITELIST = {
    "accept",
    "accept-language",
    "authorization",
    "authorize",
    "clientsource",
    "content-type",
    "route",
}


class SessionExpired(RuntimeError):
    pass


class VfsClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self.live_headers: dict[str, str] = {}

    async def __aenter__(self) -> "VfsClient":
        if not self.settings.storage_state_path.exists():
            raise FileNotFoundError(
                f"Missing {self.settings.storage_state_path}. Run vfs-france-bootstrap first."
            )

        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=self.settings.headless)
        self.context = await self.browser.new_context(
            storage_state=str(self.settings.storage_state_path)
        )
        self.page = await self.context.new_page()
        self.page.on("request", self._on_request)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    def _on_request(self, request: Request) -> None:
        if "lift-api.vfsglobal.com" not in request.url:
            return
        asyncio.create_task(self._capture_headers(request))

    async def _capture_headers(self, request: Request) -> None:
        try:
            headers = await request.all_headers()
        except Exception:
            return
        for key, value in headers.items():
            lk = key.lower()
            if lk in HEADER_WHITELIST and value:
                self.live_headers[lk] = value

    async def warm_up(self) -> None:
        assert self.page is not None
        await self.page.goto(
            self.settings.vfs_dashboard_url,
            wait_until="domcontentloaded",
            timeout=45_000,
        )
        await asyncio.sleep(2)

        current_url = self.page.url.lower()
        body = ""
        try:
            body = (await self.page.locator("body").inner_text())[:1000].lower()
        except Exception:
            pass

        looks_logged_out = (
            "/login" in current_url
            or "sign in" in body
            or "log in" in body
            or await self.page.locator('input[type="email"], input[type="password"]').count() > 0
        )
        if looks_logged_out:
            raise SessionExpired("VFS session is not authenticated")

        try:
            await self.page.goto(
                self.settings.vfs_booking_url,
                wait_until="domcontentloaded",
                timeout=45_000,
            )
            await asyncio.sleep(3)
        except Exception:
            # Dashboard session is enough for direct checks. Booking page is only a header refresh.
            pass

    async def check(self, target: TargetRequest) -> SlotResult:
        assert self.context is not None

        headers = {k.lower(): v for k, v in target.headers.items() if k.lower() in HEADER_WHITELIST}
        headers.update(self.live_headers)
        headers.setdefault("accept", "application/json, text/plain, */*")
        headers.setdefault("content-type", "application/json;charset=UTF-8")

        response = await self.context.request.post(
            target.url,
            headers=headers,
            data=target.payload,
            timeout=30_000,
        )

        status = response.status
        text = await response.text()
        try:
            data: dict[str, Any] | str = json.loads(text)
        except json.JSONDecodeError:
            data = text[:2000]

        if status in {401, 403}:
            raise SessionExpired(f"VFS API returned HTTP {status}")

        return parse_slot_response(status, data)


def parse_slot_response(http_status: int, data: dict[str, Any] | str) -> SlotResult:
    if not isinstance(data, dict):
        return SlotResult(
            status="unknown",
            available=False,
            earliest_date=None,
            http_status=http_status,
            raw=data,
        )

    earliest = data.get("earliestDate") or data.get("earliest_date")
    explicit_available = data.get("isSlotAvailable")
    if explicit_available is None:
        explicit_available = data.get("isAvailable")

    if earliest:
        return SlotResult(
            status="available",
            available=True,
            earliest_date=str(earliest),
            http_status=http_status,
            raw=data,
        )

    if explicit_available is True:
        return SlotResult(
            status="available",
            available=True,
            earliest_date=None,
            http_status=http_status,
            raw=data,
        )

    if data.get("error") or explicit_available is False or http_status == 200:
        return SlotResult(
            status="no_slots",
            available=False,
            earliest_date=None,
            http_status=http_status,
            raw=data,
        )

    return SlotResult(
        status="unknown",
        available=False,
        earliest_date=None,
        http_status=http_status,
        raw=data,
    )
