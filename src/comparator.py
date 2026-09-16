"""Звірка заголовків ukr.net і glavred.info через OpenAI.

Заголовки одних і тих самих подій у різних джерел часто сформульовані
по-різному, тому пряме порівняння рядків не працює: питаємо модель, чи
описує якийсь із заголовків glavred ту саму подію, що й кожна з трьох
новин ukr.net.
"""
from __future__ import annotations

import json

from openai import OpenAI

from . import config
from .sources.glavred import NewsItem as GlavredItem
from .sources.ukrnet import NewsItem as UkrnetItem

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ukrnet_index": {
                        "type": "integer",
                        "description": "Індекс новини ukr.net (з нуля)",
                    },
                    "covered_by_glavred": {
                        "type": "boolean",
                        "description": (
                            "true, якщо ця подія вже висвітлена якимось "
                            "заголовком glavred"
                        ),
                    },
                },
                "required": ["ukrnet_index", "covered_by_glavred"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}

_SYSTEM_PROMPT = (
    "Ти аналітик новин. Тобі дають список головних новин з ukr.net та "
    "список останніх новин з glavred.info. Заголовки можуть бути "
    "сформульовані по-різному навіть якщо йдеться про ту саму подію "
    "(різні слова, різна мова — українська/російська, різний акцент). "
    "Для кожної новини ukr.net визнач, чи є серед новин glavred та, що "
    "описує ту саму подію по суті. Відповідай лише структурованим JSON "
    "згідно зі схемою."
)


def find_uncovered(
    ukrnet_items: list[UkrnetItem], glavred_items: list[GlavredItem]
) -> list[UkrnetItem]:
    if not ukrnet_items:
        return []

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    user_content = {
        "ukrnet": [{"index": i, "title": it.title} for i, it in enumerate(ukrnet_items)],
        "glavred": [{"title": it.title} for it in glavred_items],
    }

    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_content, ensure_ascii=False)},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "coverage_check", "schema": _RESPONSE_SCHEMA, "strict": True},
        },
    )

    parsed = json.loads(response.choices[0].message.content)
    covered_indices = {
        r["ukrnet_index"] for r in parsed["results"] if r["covered_by_glavred"]
    }

    return [
        item for i, item in enumerate(ukrnet_items) if i not in covered_indices
    ]
