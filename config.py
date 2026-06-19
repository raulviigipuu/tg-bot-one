from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    admin_user_ids: set[int]


def load_config() -> Config:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    raw_admin_ids = os.getenv("ADMIN_USER_IDS")
    if not raw_admin_ids:
        raise RuntimeError("ADMIN_USER_IDS is not configured")

    admin_user_ids = parse_admin_user_ids(raw_admin_ids)

    return Config(
        telegram_bot_token=token,
        admin_user_ids=admin_user_ids,
    )


def parse_admin_user_ids(value: str) -> set[int]:
    result = set()

    for item in value.split(","):
        item = item.strip()

        if not item:
            continue

        result.add(int(item))

    return result


def is_admin(config: Config, user_id: int) -> bool:
    return user_id in config.admin_user_ids
