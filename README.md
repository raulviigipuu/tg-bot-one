# tg-bot-one

Simple Telegram bot using `python-telegram-bot` and `uv`.

Commands:

- `/start`
- `/help`
- `/status`
- `/user`

## Setup

Requires Python 3.13+ and `uv`.

```bash
uv python install 3.13
uv python pin 3.13
uv sync
```

Create `.env`:

```env
TELEGRAM_BOT_TOKEN=123456789:replace_with_your_bot_token
ADMIN_USER_IDS=123456789,987654321
```

## Run

```bash
uv run python main.py
```

Stop with `Ctrl+C`.

## Dependencies

```bash
uv add package-name
uv add --dev package-name
uv remove package-name
uv lock --upgrade
uv sync
```

## Files

```text
main.py         # Bot entry point and command handlers
config.py       # Environment configuration
pyproject.toml  # Project metadata and dependencies
uv.lock         # Locked dependency versions
```
