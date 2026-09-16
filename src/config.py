import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Відсутня обов'язкова змінна оточення: {name}")
    return value


TELEGRAM_BOT_TOKEN = _require("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _require("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = _require("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
CHECK_INTERVAL_MINUTES = int(os.environ.get("CHECK_INTERVAL_MINUTES", "30"))
STATE_FILE = os.environ.get("STATE_FILE", "state.json")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

UKRNET_START_URL = "https://www.ukr.net/ajax/start.json"
UKRNET_MAIN_SECTION_SEO = "main"  # розділ "Головне" у відповіді start.json

GLAVRED_MAIN_NEWS_URL = "https://glavred.info/detail/main_news"
GLAVRED_ITEMS_LIMIT = 10
