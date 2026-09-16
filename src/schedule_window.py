"""Перевірка, чи зараз "робочі" години бота.

Правило:
- будні (пн–пт): з 6:00 до 1:00 наступної доби;
- вихідні (сб, нд): з 7:00 до 23:00.

Нічна частина будньої доби (0:00–1:00) належить попередній добі: активна,
лише якщо ця попередня доба сама була буднім днем (тобто це "нічне
продовження" робочого дня, а не старт нового дня).
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from . import config

TIMEZONE = ZoneInfo(config.SCHEDULE_TIMEZONE)

_WEEKDAY_START_HOUR = 6
_WEEKDAY_END_HOUR = 1  # наступної доби
_WEEKEND_START_HOUR = 7
_WEEKEND_END_HOUR = 23

_WEEKDAYS = {0, 1, 2, 3, 4}  # datetime.weekday(): пн=0 ... нд=6


def is_active_now(now: datetime | None = None) -> bool:
    if now is None:
        now = datetime.now(TIMEZONE)
    else:
        now = now.astimezone(TIMEZONE)

    hour_frac = now.hour + now.minute / 60

    if hour_frac < _WEEKDAY_END_HOUR:
        yesterday = (now.weekday() - 1) % 7
        return yesterday in _WEEKDAYS

    if now.weekday() in _WEEKDAYS:
        return hour_frac >= _WEEKDAY_START_HOUR

    return _WEEKEND_START_HOUR <= hour_frac < _WEEKEND_END_HOUR
