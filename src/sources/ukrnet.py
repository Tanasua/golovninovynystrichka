"""Отримання трьох головних новин з ukr.net.

ukr.net рендерить стрічку новин на клієнті через JS-шаблон, тому HTML
головної сторінки порожній. Реальні дані бере фронтенд з
https://www.ukr.net/ajax/start.json — саме цей JSON-ендпоінт викликаємо
напряму, це набагато стабільніше за парсинг чи headless-браузер.
"""
from __future__ import annotations

from dataclasses import dataclass

import requests

from .. import config


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str


def fetch_top3() -> list[NewsItem]:
    response = requests.get(
        config.UKRNET_START_URL,
        headers={"User-Agent": config.USER_AGENT, "Accept": "application/json"},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    sections = data.get("news", [])
    main_section = next(
        (s for s in sections if s.get("seo") == config.UKRNET_MAIN_SECTION_SEO),
        None,
    )
    if main_section is None:
        # запасний варіант, якщо ukr.net змінить seo-код розділу
        main_section = next(
            (s for s in sections if s.get("title") == "Головне"), None
        )
    if main_section is None:
        raise RuntimeError(
            "Не вдалося знайти розділ 'Головне' у відповіді ukr.net/ajax/start.json "
            "— можливо, змінилась структура відповіді"
        )

    items = main_section.get("items", [])[:3]
    return [NewsItem(title=item["title"], url=item["url"]) for item in items]
