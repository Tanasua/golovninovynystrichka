"""Надсилання повідомлень у Telegram."""
from __future__ import annotations

import html
import random

import requests

from . import config
from .sources.ukrnet import NewsItem

INTRO_PHRASES = [
    "це нам цікаво?",
    "глянемо на це?",
    "може, візьмемо цю тему?",
    "новини на розгляд",
    "це може бути в нас",
    "на замітку редакції",
    "варто глянути",
    "це нам підходить?",
    "можливо, наше",
    "це може зацікавити",
    "звернемо увагу?",
    "це в тему?",
    "свіже і, можливо, наше",
    "це наш формат?",
    "на оцінку редакції",
]


def _escape(text: str) -> str:
    return html.escape(text, quote=False)


def send_uncovered_news(items: list[NewsItem]) -> None:
    if not items:
        return

    blocks = [random.choice(INTRO_PHRASES)]
    for item in items:
        link = f'<a href="{_escape(item.url)}">лінк</a>'
        blocks.append(f"{_escape(item.title)} ({link})")
    text = "\n\n".join(blocks)

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "link_preview_options": {"is_disabled": True},
        },
        timeout=15,
    )
    response.raise_for_status()
