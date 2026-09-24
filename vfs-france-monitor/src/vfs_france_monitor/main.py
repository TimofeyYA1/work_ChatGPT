from __future__ import annotations

import asyncio

from .config import load_settings
from .monitor import run_monitor


def cli() -> None:
    asyncio.run(run_monitor(load_settings()))


if __name__ == "__main__":
    cli()
