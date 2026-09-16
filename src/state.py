"""Локальний стан бота: які новини ukr.net уже були надіслані в Telegram,
щоб не дублювати сповіщення про ту саму новину на кожному наступному циклі
(поки glavred її не напише)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from . import config

_RETENTION_SECONDS = 3 * 24 * 60 * 60  # 3 дні


def _load() -> dict:
    path = Path(config.STATE_FILE)
    if not path.exists():
        return {"notified": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"notified": {}}


def _save(state: dict) -> None:
    Path(config.STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def filter_already_notified(urls: list[str]) -> list[str]:
    state = _load()
    notified = state.get("notified", {})
    return [u for u in urls if u not in notified]


def mark_notified(urls: list[str]) -> None:
    state = _load()
    notified = state.get("notified", {})
    now = time.time()
    for u in urls:
        notified[u] = now

    cutoff = now - _RETENTION_SECONDS
    notified = {u: ts for u, ts in notified.items() if ts >= cutoff}

    state["notified"] = notified
    _save(state)
