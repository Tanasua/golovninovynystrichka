"""Надсилання повідомлень у Telegram."""
from __future__ import annotations

import html

import requests

from . import config
from .sources.ukrnet import NewsItem


def _escape(text: str) -> str:
    return html.escape(text, quote=False)


def send_uncovered_news(items: list[NewsItem]) -> None:
    if not items:
        return

    blocks = ["нам це цікаво?"]
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
