"""Отримання останніх новин з розділу "Головне за день" на glavred.info."""
from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from .. import config


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str


def fetch_latest(limit: int = config.GLAVRED_ITEMS_LIMIT) -> list[NewsItem]:
    response = requests.get(
        config.GLAVRED_MAIN_NEWS_URL,
        headers={"User-Agent": config.USER_AGENT},
        timeout=15,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items: list[NewsItem] = []
    for block in soup.select("div.rubric-full-list__item"):
        link = block.select_one("a.rubric-full-list__title")
        if link is None or not link.get("href"):
            continue
        title = link.get_text(strip=True)
        if not title:
            continue
        items.append(NewsItem(title=title, url=link["href"]))
        if len(items) >= limit:
            break

    if not items:
        raise RuntimeError(
            "Не вдалося знайти новини на glavred.info/detail/main_news "
            "— можливо, змінилась верстка сторінки"
        )

    return items
