# VFS France Russia Slot Monitor

Personal MVP for monitoring France visa appointment slots in VFS Global Russia and sending immediate Telegram alerts.

## What this MVP does

- works with the France / Russia VFS portal (`rus/en/fra`);
- uses your real authenticated browser session;
- during one manual setup, captures the exact VFS request used to check availability;
- replays that request at a conservative interval instead of clicking through the full UI every time;
- supports multiple centres / visa categories;
- notifies Telegram only when a slot appears or changes;
- persists state to avoid duplicate alerts;
- detects expired sessions and asks for a manual refresh instead of trying to defeat CAPTCHA / Turnstile;
- can run continuously in Docker on a VPS.

It intentionally **does not auto-book appointments**. The MVP goal is fast and reliable detection first.

## Why this design

VFS is a JavaScript application. DOM selectors and page layout can change, while the browser still calls the same backend service to check availability. The bootstrap step listens for the real `CheckIsSlotAvailable` request after you manually choose a centre/category and stores its request body locally.

The monitor then checks the same target inside your authenticated Playwright browser context. This is faster than navigating the complete booking wizard every cycle and means centre/category IDs do not need to be hardcoded.

## Project layout

```text
src/vfs_france_monitor/
  bootstrap.py   # manual login + capture target requests
  monitor.py     # scheduler, dedup, heartbeat, retries
  vfs.py         # Playwright session + slot API client
  notifier.py    # Telegram sender
  storage.py     # local JSON state
  config.py      # environment configuration
```

Runtime secrets and session data live under `data/` and are gitignored.

## 1. Install locally

Python 3.11+ is required.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -e .
playwright install chromium
cp .env.example .env
```

Export the values from `.env` in your shell, or use any dotenv loader you prefer. The application itself deliberately has no dotenv dependency.

## 2. Create Telegram alerts

Create a Telegram bot through BotFather and put its token and your chat ID into the environment:

```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
```

If these are omitted, messages are printed to stdout instead. That is useful during setup.

## 3. Capture your VFS session and targets

Run this on a computer with a GUI:

```bash
vfs-france-bootstrap
```

A Chromium window opens.

1. Sign in to VFS normally.
2. Start a new booking.
3. Select the visa application centre, category and subcategory you need.
4. Wait until VFS performs its availability check. The terminal will print `Captured VFS slot check`.
5. If you want to monitor another city, change the centre and let VFS check it too.
6. Return to the terminal and press Enter.
7. Give each captured target a readable name, for example `Moscow / Short Stay / Other`.

The command creates:

```text
data/storage_state.json  # cookies + localStorage; SECRET
data/targets.json        # captured API request templates; SECRET
data/monitor_state.json  # created later by monitor
```

Never commit the `data/` directory.

### Recommended target strategy

For a personal monitor, start with only the centres you would genuinely travel to. Fewer targets means quicker cycles and fewer requests to VFS. A sensible first setup is your primary centre plus 1-3 acceptable alternatives.

## 4. Start monitoring

```bash
vfs-france-monitor
```

Default behavior:

- one monitoring cycle every ~75 seconds;
- random jitter of ±15 seconds;
- 2.5 seconds between target checks;
- heartbeat every 6 hours;
- session check every 20 cycles;
- Telegram alert on a new/changed available slot;
- 10-minute retry when the VFS session expires.

Tune with environment variables:

```bash
CHECK_INTERVAL_SECONDS=75
CHECK_JITTER_SECONDS=15
PER_TARGET_DELAY_SECONDS=2.5
HEARTBEAT_HOURS=6
```

Do not set an aggressively small interval. Faster polling is not automatically better if it gets the session rate-limited or blocked.

## 5. Run on a VPS

First perform `vfs-france-bootstrap` locally, then copy only the generated `data/` directory to the VPS alongside the project.

```bash
cp .env.example .env
# fill TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
docker compose up -d --build
docker compose logs -f monitor
```

The compose file mounts `./data` into the container and restarts the monitor automatically.

When Telegram says the VFS session expired, run bootstrap again locally and replace `data/storage_state.json` (and `targets.json` if you changed centres).

## Slot detection logic

The VFS availability response observed by current open-source implementations contains an `earliestDate` field. This monitor treats:

- non-empty `earliestDate` as **available**;
- explicit `isSlotAvailable=true` / `isAvailable=true` as **available**;
- a normal 200 response without a date, or a VFS `error` indicating no availability, as **no slots**;
- malformed/non-JSON responses as **unknown**, never as a slot.

HTTP 401/403 is treated as an expired or invalid session.

## Reliability choices

- **Network request capture instead of hardcoded IDs.** Your actual VFS choices become the configuration.
- **Session reuse.** No repeated automated login attempts.
- **No CAPTCHA bypass.** Login challenges stay manual.
- **Jitter + sane interval.** Reduces synchronized hammering and unnecessary traffic.
- **Transition-based alerts.** No Telegram spam every cycle.
- **Atomic JSON writes.** State files are replaced atomically to reduce corruption after a crash.
- **Docker restart policy.** The process comes back after VPS/container restarts.

## Known limitations of MVP

1. VFS can change its API contract, headers, or authentication flow at any time.
2. VFS sessions expire. The monitor deliberately requires manual re-bootstrap rather than automating challenge solving.
3. We cannot fully validate Russia→France request payloads without a real VFS account/session. Bootstrap captures them from your browser specifically to avoid guessing them.
4. Availability detection is not a reservation. A slot can disappear before you open the site.
5. This project does not bypass queues, CAPTCHAs, access controls, or booking/payment safeguards.

## Tests

```bash
pip install -e '.[dev]'
pytest
```

## Next milestone after MVP

Once slot detection is stable for several days, the next useful increment is a Telegram control layer (`/status`, `/pause`, `/resume`, `/check`) and per-target date filters. Auto-booking should be considered only after the monitoring path is proven reliable.
