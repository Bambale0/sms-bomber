# sms-bomber

Production-oriented asynchronous Telegram bot scaffold for **authorized notification/API testing**.

> This repository intentionally does not implement SMS flooding, OTP abuse, proxy-based block evasion, or requests to third-party services without permission. Targets must be explicitly configured and their host must be allowlisted.

## Architecture

```text
app/
├── main.py
├── config.py
├── bot/
│   └── handlers/
│       └── user.py
├── infrastructure/
│   ├── http.py
│   └── logging.py
└── services/
    ├── engine.py
    └── targets/
        ├── base.py
        └── sandbox.py
```

The bot uses:

- `aiogram` for Telegram updates;
- one long-lived `aiohttp.ClientSession` for outbound I/O;
- bounded concurrency through `asyncio.Semaphore`;
- retry with exponential backoff for transient failures;
- explicit target-host allowlisting;
- typed result objects and structured logs;
- graceful HTTP-session shutdown.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
cp .env.example .env
```

Set a Telegram bot token in `.env`. By default, only `localhost` and `127.0.0.1` are permitted target hosts.

Start a local test endpoint at the configured `SANDBOX_TARGET_URL`, then run:

```bash
python -m app.main
```

## Bot flow

1. `/start` explains that only authorized test endpoints are supported.
2. User sends a phone-like test identifier in `7XXXXXXXXXX` format.
3. The engine executes the configured allowlisted targets concurrently.
4. The bot reports per-run success/failure totals without exposing sensitive response bodies.

The phone-like value is treated as test data. Do not send real personal data to endpoints unless you have a lawful basis and permission to do so.

## Verification

```bash
python -m pytest
python -m compileall -q app tests
ruff check .
```
